# -*- coding: utf-8 -*-

import imp, json, logging, os, pprint, time, types
import requests
from . import logger_setup
from .auth import Authenticator
from .request import Requester
from .search import Searcher


log = logging.getLogger(__name__)
logger_setup.check_logger()


class BorrowDirect( object ):
    """ Manages high-level function calls. """

    def __init__( self, settings=None, logger=None ):
        """
        - Allows a settings module to be passed in,
            or a settings path to be passed in,
            or a dictionary to be passed in. """
        ## general initialization
        self.API_URL_ROOT = None
        self.API_KEY = None
        self.PARTNERSHIP_ID = None
        self.UNIVERSITY_CODE = None
        self.PICKUP_LOCATION = None
        self.LOG_PATH = None
        self.LOG_LEVEL = None
        ## setup
        bdh = BorrowDirectHelper()
        normalized_settings = bdh.normalize_settings( settings )
        bdh.update_properties( self, normalized_settings )
        bdh.setup_log( self, logger )
        ## updated by workflow
        self.AId = None
        self.authnz_valid = None
        self.search_result = None
        self.request_result = None

    def run_auth_nz( self, patron_barcode ):
        """ Runs authN/Z and stores authentication-id.
            Can be called manually, but likely no need to, since run_search() and run_request_exact_item() handle auth automatically. """
        log.debug( 'starting run_auth_nz()...' )
        authr = Authenticator()
        self.AId = authr.authenticate(
            patron_barcode, self.API_URL_ROOT, self.API_KEY, self.PARTNERSHIP_ID, self.UNIVERSITY_CODE )
        time.sleep( 1 )
        self.authnz_valid = authr.authorize(
            self.API_URL_ROOT, self.AId )
        log.info( 'run_auth_nz() complete' )
        return

    def run_search_exact_item( self, patron_barcode, search_type, search_value ):
        """ Searches for exact key-value.
            Called manually. """
        log.debug( '\n\nstarting run_search_exact_item()...' )
        srchr = Searcher()
        self.search_result = srchr.search_exact_item( patron_barcode, self.API_URL_ROOT, self.API_KEY, self.PARTNERSHIP_ID, self.UNIVERSITY_CODE, search_type, search_value )
        log.debug( 'search_result, ```%s```' % pprint.pformat(self.search_result) )
        log.info( 'run_search_exact_item() complete' )
        return

    def run_search_bib_item( self, patron_barcode, title, author, year ):
        """ Searches for bib item.
            Called manually. """
        log.debug( '\n\nstarting run_search_bib_item()...' )
        srchr = Searcher()
        self.search_result = srchr.search_bib_item( patron_barcode, self.API_URL_ROOT, self.API_KEY, self.PARTNERSHIP_ID, self.UNIVERSITY_CODE, title, author, year )
        log.debug( 'search_result, ```%s```' % pprint.pformat(self.search_result) )
        log.info( 'run_search_bib_item() complete' )
        return

    def run_request_exact_item( self, patron_barcode, search_type, search_value ):
        """ Runs an 'ExactSearch' query.
            <https://relais.atlassian.net/wiki/spaces/ILL/pages/106608984/RequestItem#RequestItem-RequestItemrequestjson>
            Called manually. """
        log.debug( '\n\nstarting run_exact_item_request()...' )
        req = Requester()
        self.request_result = req.request_exact_item( patron_barcode, self.API_URL_ROOT, self.API_KEY, self.PARTNERSHIP_ID, self.UNIVERSITY_CODE, self.PICKUP_LOCATION, search_type, search_value )
        log.info( 'run_request_exact_item() complete' )
        return

    def run_request_bib_item( self, patron_barcode, title, author, year ):
        """ Runs a 'BibSearch' query.
            <https://relais.atlassian.net/wiki/spaces/ILL/pages/106608984/RequestItem#RequestItem-RequestItemrequestjson>
            Called manually. """
        log.debug( '\n\nstarting run_bib_search_request()...' )
        log.debug( 'title, ```%s```' % title )
        req = Requester()
        self.request_result = req.request_bib_item( patron_barcode, self.API_URL_ROOT, self.API_KEY, self.PARTNERSHIP_ID, self.UNIVERSITY_CODE, self.PICKUP_LOCATION, title, author, year )
        log.info( 'run_request_bib_item() complete' )
        return

    ## end class BorrowDirect


class BorrowDirectHelper( object ):
    """ Assists BorrowDirect setup.
        Called by BorrowDirect.__init__() """

    def normalize_settings( self, settings ):
        """ Returns a settings module regardless whether settings are passed in as a module or dict or settings-path.
            Called by BorrowDirect.__init__() """
        log.debug( 'type(settings), ```%s```' % type(settings) )
        assert ( isinstance(settings, dict) or isinstance(settings, str) or isinstance(settings, types.ModuleType) or settings == None  ), Exception( 'Passing in settings is optional, but if used, must be either a dict, a path to a settings module, or a module named settings; current type is: %s' % type(settings) )
        if isinstance( settings, dict ):
            s = imp.new_module( 'settings' )
            for k, v in settings.items():
                setattr( s, k, v )
            settings = s
        elif isinstance( settings, str ):  # path
              settings = imp.load_source( '*', settings )
        return settings

    def update_properties( self, bd_instance, settings ):
        """ Sets main properties.
            Called by BorrowDirect.__init__() """
        bd_instance.API_URL_ROOT = None if ( 'API_URL_ROOT' not in dir(settings) ) else settings.API_URL_ROOT
        bd_instance.API_KEY = None if ( 'API_KEY' not in dir(settings) ) else settings.API_KEY
        bd_instance.PARTNERSHIP_ID = None if ( 'PARTNERSHIP_ID' not in dir(settings) ) else settings.PARTNERSHIP_ID
        bd_instance.UNIVERSITY_CODE = None if ( 'UNIVERSITY_CODE' not in dir(settings) ) else settings.UNIVERSITY_CODE
        bd_instance.PICKUP_LOCATION = None if ( 'PICKUP_LOCATION' not in dir(settings) ) else settings.PICKUP_LOCATION
        bd_instance.LOG_PATH = None if ( 'LOG_PATH' not in dir(settings) ) else settings.LOG_PATH
        bd_instance.LOG_LEVEL = 'DEBUG' if ( 'LOG_LEVEL' not in dir(settings) ) else settings.LOG_LEVEL
        return

    def setup_log( self, bd_instance, logger ):
        """ Configures log path and level.
            Called by BorrowDirect.__init__() """
        if logger:
            bd_instance.logger = logger
        else:
            log_level = {
                'DEBUG': logging.DEBUG, 'INFO': logging.INFO, }
            logging.basicConfig(
                filename=bd_instance.LOG_PATH, level=log_level[bd_instance.LOG_LEVEL],
                format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
                datefmt='%d/%b/%Y %H:%M:%S' )
            bd_instance.logger = logging.getLogger(__name__)
        return

    ## end class BorrowDirectHelper
