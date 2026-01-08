"""
The WAMP portion of the DECS<->VISA implementation
"""
import asyncio
import queue
import typing

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import exception as wamp_exceptions
from autobahn.wamp import auth
from autobahn.wamp.message import Welcome
from autobahn.wamp.types import CloseDetails
from autobahn.wamp.types import CallResult

from decs_visa_tools.base_logger import logger
from decs_visa_tools.command_parser import decs_command_parser, decs_request_parser
from decs_visa_tools.response_parser import decs_response_parser

# shutdown message
from decs_visa_tools.decs_visa_settings import SHUTDOWN

class Component(ApplicationSession):
    """
    An application component that connects to a WAMP realm.
    """
    #is_controllable = False
    #existing_controller = False

    def onWelcome(self, welcome: Welcome) -> str | None:
        logger.info("Established session: %s", str(welcome.session))
        return super().onWelcome(welcome)

    def onConnect(self):
        user=self.config.extra['user_name']
        logger.info("WAMP connection made")
        try:
            self.join(self.config.realm, ["wampcra"], user)
        except Exception as e:
            logger.info("Failed to establish a WAMP session: %s", e)
            self.leave()

    def onChallenge(self, challenge):
        user=self.config.extra['user_name']
        logger.info("Starting WAMP-CRA authentication on realm '%s' as user '%s'",
                    self.config.realm, user)
        user_secret=self.config.extra['user_secret']
        if challenge.method == "wampcra":
            logger.debug("WAMP-CRA challenge received: %s", challenge)
            if 'salt' in challenge.extra:
                # salted secret
                key = auth.derive_key(user_secret,
                                        challenge.extra['salt'],
                                        challenge.extra['iterations'],
                                        challenge.extra['keylen'])
            else:
                # plain, unsalted secret
                key = user_secret
            # compute signature for challenge, using the key
            signature = auth.compute_wcs(key, challenge.extra['challenge'])
            # return the signature to the router for verification
            logger.debug("WAMP-CRA challenge response: %s", signature)
            return signature
        raise NotImplementedError(f"Invalid authmethod {challenge.method}")
    
    async def onJoin(self, details):
    # Once the WAMP session is open, the session still has to
    # claim control of the system.  This could fail for several reasons.
    # Somebody else may already have a controlling session, or the system
    # could be in local mode etc

        # Try to establish a controlling WAMP session with the router
        if await self.claim_system_control():
            logger.info("Ready to process WAMP RPCs")
            # start processing the server queue
            await self.process_queue()

        # queue processing is closing down
        logger.info("WAMP closing session")
        try:
            # Might error if not controlling, but as we're leaving anyway...
            await self.checked_rpc('oi.decs.sessionmanager.relinquish_system_control')
        except Exception:
            pass
        self.leave()

    def onLeave(self, details: CloseDetails):
        logger.info("Leaving WAMP session: %s", details.reason)
        return super().onLeave(details)

    def onDisconnect(self):
        # If user attempts Keyboard interrupt, this will
        # shutdown the socket_server as the WAMP component
        # stops
        r=self.config.extra['output_queue']
        try:
            _ = r.get_nowait()
        except queue.Empty:
            pass
        r.put(SHUTDOWN)
        logger.info("Stopping WAMP event_loop")
        asyncio.get_event_loop().stop()

    def package_plain_response(self, value: typing.Any) -> CallResult:
        """
        Short function to work around a WAMP (non?)feature that
        allows 'simple' responses to be flattened aspassed back
        'bare' ratherthan  as part of a response.results dictionary.

        This repackages them as CallResults to allow consistent
        handling of responses
        """
        packaged_response = CallResult()
        packaged_response.results = [value, ]
        return packaged_response

    async def checked_rpc(self, rpc_uri):
        """
        Wraps a WAMP rRPC call with logging and error checking
        """
        logger.debug("get_ request uri: \"%s\"", str(rpc_uri))
        try:
            resp = await self.call(rpc_uri)
            if not isinstance(resp, CallResult):
                resp = self.package_plain_response(resp)
            logger.debug("WAMP response: %s", str(resp.results))
            return resp
        except wamp_exceptions.ApplicationError as e:
            logger.info("WAMP call ApplicationError: %s", e.error_message())
            raise
        except Exception as e:
            logger.info("WAMP call failed: %s", e)
            raise

    async def checked_rpc_args(self, rpc_uri, args):
        """
        Wraps a WAMP rRPC call including args with logging and error checking
        """
        logger.debug("set_ command uri: \"%s\" args: %s", str(rpc_uri), str(args))
        try:
            resp = await self.call(rpc_uri, *args)
            if not isinstance(resp, CallResult):
                resp = self.package_plain_response(resp)
            logger.debug("WAMP response: %s", str(resp.results))
            return resp
        except wamp_exceptions.ApplicationError as e:
            logger.info("WAMP call ApplicationError: %s", e.error_message())
            raise
        except Exception as e:
            logger.info("WAMP call Error: %s", e)
            raise
        

    async def checked_publication(self, rpc_uri, args):
        """
        Wraps a WAMP topic publication with logging and error checking
        """
        logger.debug("Publication uri: \"%s\" args: %s", str(rpc_uri), str(args))
        try:
            self.publish(rpc_uri, *args)
        except (Exception) as e:
            logger.info("WAMP publication Error: %s", e)
            raise
        logger.debug("Publication made")

    async def claim_system_control(self) -> bool:
        """
        Attempt to establish a controlling
        WAMP session with the router
        """
        logger.info("Attempt to establish a controlling session")
        try:
            # is the system in remote mode?
            resp = await self.checked_rpc('oi.decs.sessionmanager.system_control_mode')
            is_controllable = int(resp.results[0]) == 1
            if not is_controllable:
                logger.info("DECS system is not in remote control mode")
                return False
            resp = await self.checked_rpc('oi.decs.sessionmanager.system_controller')
            existing_controller = int(resp.results[0]) != 0
            if existing_controller:
                logger.info("DECS system is under control: %s", str(resp.results[1]))
                return False
            resp = await self.checked_rpc('oi.decs.sessionmanager.claim_system_control')
            if resp.results[1] != self.config.extra['user_name']:
                logger.info("Failed to claim system control")
                return False
            return True
        except wamp_exceptions.ApplicationError as e:
            logger.info("WAMP ApplicationError during establishment of controlling session: %s", e.error_message())
        except Exception as e:
            logger.info("Error during establishment of controlling session: %s", e)
        return False

    async def process_queue(self) -> None:
        """
        Monitor the message queue and process the
        WAMP queries as required.
        """
        q=self.config.extra['input_queue']
        r=self.config.extra['output_queue']
        can_run = True
        while can_run:
            try:
                data = q.get_nowait()
                if data == SHUTDOWN:
                    logger.info("WAMP shutdown request from queue")
                    break
                # set something
                if "set_" in data:
                    # It's a command, so
                    try:
                        rpc_uri, args = decs_command_parser(data)
                    except (ValueError, NotImplementedError) as e:
                        # Unknown command / bad arguments / not yet
                        # implemented - as nothing has ben sent
                        # to WAMP there will be no WAMP level error,
                        # so we can just return this error message to
                        # the client
                        r.put(e)
                    else:
                        try:
                            resp = await self.checked_rpc_args(rpc_uri, args)
                            # Determine what is returned
                            r.put(decs_response_parser(resp))
                        except Exception as e:
                            logger.info("WAMP error: %s", e)
                            # This is a WAMP level error - probably
                            # nothing we can do to fix this, so
                            can_run = False

                # get a parameter
                elif "get_" in data:
                    # It's a request, so
                    try:
                        rpc_uri = decs_request_parser(data)
                    except ValueError as e:
                        # Unknown request as nothing has ben sent
                        # to WAMP there will be no WAMP level error,
                        # so we can just return this error message to
                        # the client
                        r.put(e)
                    else:
                        try:
                            resp = await self.checked_rpc(rpc_uri)
                            # Determine what is returned
                            r.put(decs_response_parser(resp))
                        except Exception as e:
                            logger.info("WAMP error: %s", e)
                            # This is a WAMP level error - probably
                            # nothing we can do to fix this, so
                            can_run = False

                # publish something
                elif "PUBLISH" in data:
                    try:
                        rpc_uri, args = decs_command_parser(data)
                    except (ValueError, NotImplementedError) as e:
                        # Unknown command / bad arguments / not yet
                        # implemented - as nothing has ben sent
                        # to WAMP there will be no WAMP level error,
                        # so we can just return this error message to
                        # the client
                        r.put(e)
                    else:
                        try:
                            resp = await self.checked_publication(rpc_uri, args)
                            # can just assume this has publication has
                            # been made
                            r.put("PUBLISHED")
                        except Exception as e:
                            logger.info("WAMP error: %s", e)
                            # This is a WAMP level error - probably
                            # nothing we can do to fix this, so
                            can_run = False

                elif "IDN" in data:
                    # Process the IDN query as correctly as we can.
                    # Left as a special case here as multiple WAMP calls
                    # are required to collate all the required data
                    try:
                        rpc_uri = 'oi.decs.host.name'
                        host_name_full = await self.checked_rpc(rpc_uri)
                        host_name = str(host_name_full.results[0])
                        logger.debug("Extractracted values: %s", host_name)
                        rpc_uri = 'oi.decs.host.decs_version'
                        host_version_full = await self.checked_rpc(rpc_uri)
                        version = str(host_version_full.results[0])
                        logger.debug("Extractracted values: %s", version)
                        idn_string = f"QD - Oxford, oi.DECS, {host_name}, {version}"
                        logger.debug("IDN string: %s", idn_string)
                        r.put(idn_string)
                    except Exception:
                        can_run = False

                else:
                    # unknown command
                    logger.info("Unkown command: %s", str(data))
                    r.put(f"Unkown command: {str(data)}")

            except queue.Empty:
                await asyncio.sleep(0.0005)
                continue
            except Exception as e:
                # Something bad has happened to the WAMP connection
                # perhaps Admin has put the system into local mode...?
                can_run = False
