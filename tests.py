# -*- coding: utf-8 -*-

import imp, logging, pprint, os, time, unittest
from bdpy3 import BorrowDirect, logger_setup
from bdpy3.auth import Authenticator
from bdpy3.search import Searcher
from bdpy3.request import Requester


SLEEP_SECONDS = 2  # being nice

log = logging.getLogger(__name__)
logger_setup.check_logger()


class BorrowDirectTests( unittest.TestCase ):

    def setUp(self):
        time.sleep( SLEEP_SECONDS )
        self.patron_barcode = os.environ['BDPY3_TEST__PATRON_BARCODE']
        self.api_url_root = os.environ['BDPY3_TEST__API_URL_ROOT']
        self.api_key = os.environ['BDPY3_TEST__API_KEY']
        self.university_code = os.environ['BDPY3_TEST__UNIVERSITY_CODE']
        self.partnership_id = os.environ['BDPY3_TEST__PARTNERSHIP_ID']
        self.pickup_location = os.environ['BDPY3_TEST__PICKUP_LOCATION']
        self.isbn_found_and_available = os.environ['BDPY3_TEST__ISBN_FOUND_AND_AVAILABLE']
        self.isbn_found_and_unavailable = os.environ['BDPY3_TEST__ISBN_FOUND_AND_UNAVAILABLE']
        self.isbn_not_found = os.environ['BDPY3_TEST__ISBN_NOT_FOUND']

    def test_settings_instantiation(self):
        """ Tests that instance instantiation handles settings not-defined, or defined as dict, module, or path. """
        ## no settings passed on instantiation
        bd = BorrowDirect()  # no settings info
        self.assertEqual(
            True, isinstance(bd, BorrowDirect) )
        ## dict settings
        settings_dict = {}  ## empty dct
        bd = BorrowDirect( settings_dict )
        self.assertEqual(
            None, bd.UNIVERSITY_CODE )
        settings_dict = { 'UNIVERSITY_CODE': '123' }  ## populated dct
        bd = BorrowDirect( settings_dict )
        self.assertEqual(
            '123', bd.UNIVERSITY_CODE )
        ## module settings
        s = imp.new_module( 'settings' )  ## empty module
        bd = BorrowDirect( s )
        self.assertEqual(
            None, bd.UNIVERSITY_CODE )
        s = imp.new_module( 'settings' )  ## populated module
        s.UNIVERSITY_CODE = '234'
        bd = BorrowDirect( s )
        self.assertEqual(
            '234', bd.UNIVERSITY_CODE )

    def test_run_auth_nz(self):
        """ Tests manager authN/Z. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
        }
        bd = BorrowDirect( basics )
        bd.run_auth_nz( self.patron_barcode )
        self.assertEqual(
            True, bd.authnz_valid )

    def test_run_search_exact_item__found_and_available(self):
        """ Tests search for item found and available. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
        }
        bd = BorrowDirect( basics )
        bd.run_search_exact_item( self.patron_barcode, 'ISBN', self.isbn_found_and_available )
        self.assertEqual( ['Available', 'OrigNumberOfRecords', 'PickupLocation', 'RequestLink'], sorted(bd.search_result.keys()) )
        self.assertEqual( True, bd.search_result['Available'] )

    def test_run_search_exact_item__found_and_unavailable(self):
        """ Tests search for item found and unavailable. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
        }
        bd = BorrowDirect( basics )
        bd.run_search_exact_item( self.patron_barcode, 'ISBN', self.isbn_found_and_unavailable )
        self.assertEqual( ['Available', 'OrigNumberOfRecords', 'RequestLink'], sorted(bd.search_result.keys()) )
        self.assertEqual( False, bd.search_result['Available'] )

    def test_run_search_exact_item__not_found(self):
        """ Tests search for item not found. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
        }
        bd = BorrowDirect( basics )
        bd.run_search_exact_item( self.patron_barcode, 'ISBN', self.isbn_not_found )
        self.assertEqual(
            {"Problem":{"ErrorCode":"PUBFI002","ErrorMessage":"No result"}}, bd.search_result )

    # def test_run_request_exact_item__found_and_available(self):
    #     """ Tests manager requesting.
    #         Commented out because it'll really request the item. """
    #     basics = {
    #         'API_URL_ROOT': self.api_url_root,
    #         'API_KEY': self.api_key,
    #         'PARTNERSHIP_ID': self.partnership_id,
    #         'UNIVERSITY_CODE': self.university_code,
    #         'PICKUP_LOCATION': self.pickup_location,
    #         'LOG_PATH': self.LOG_PATH }
    #     bd = BorrowDirect( basics )
    #     bd.run_request_exact_item( self.patron_barcode, 'ISBN', self.isbn_found_and_available )
    #     self.assertEqual(
    #         ['RequestNumber'], sorted(bd.request_result.keys()) )
    #     self.assertEqual(
    #         'BRO-', bd.request_result['RequestNumber'][0:4] )

    def test_run_search_bib_item__found_and_available(self):
        """ Tests search for item found and available. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
        }
        bd = BorrowDirect( basics )
        ( title, author, year ) = ( 'Zen and the art of motorcycle maintenance - an inquiry into values', ['Pirsig, Robert M'], '1974' )
        bd.run_search_bib_item( self.patron_barcode, title, author, year )
        self.assertEqual( ['Available', 'OrigNumberOfRecords', 'PickupLocation', 'RequestLink'], sorted(bd.search_result.keys()) )
        self.assertEqual( True, bd.search_result['Available'] )

    def test_run_request_exact_item__not_found(self):
        """ Tests manager exact-item requesting on not-found item.
            NOTE THAT THIS WILL REALLY ATTEMPT THE REQUEST. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
            'PICKUP_LOCATION': self.pickup_location,
        }
        bd = BorrowDirect( basics )
        bd.run_request_exact_item( self.patron_barcode, 'ISBN', self.isbn_not_found )
        self.assertEqual(
            {'Problem': {'ErrorCode': 'PUBRI003', 'ErrorMessage': 'No result'}}, bd.request_result )

    def test_run_request_bib_item__not_found(self):
        """ Tests manager bib-item requesting.
            NOTE THAT THIS WILL REALLY ATTEMPT THE REQUEST. """
        basics = {
            'API_URL_ROOT': self.api_url_root,
            'API_KEY': self.api_key,
            'PARTNERSHIP_ID': self.partnership_id,
            'UNIVERSITY_CODE': self.university_code,
            'PICKUP_LOCATION': self.pickup_location,
        }
        bd = BorrowDirect( basics )
        ( title, author, year ) = ( 'Zen and the art of motorcycle maintenance - an inquiry into values', ['Pirsig, Robert M'], '1874' )
        log.debug( 'title, ```%s```' % title )
        bd.run_request_bib_item( self.patron_barcode, title, author, year )
        self.assertEqual(
            {'Problem': {'ErrorCode': 'PUBRI003', 'ErrorMessage': 'No result'}},
            bd.request_result
        )

    ## end class BorrowDirectTests


class AuthenticatorTests( unittest.TestCase ):

    def setUp(self):
        time.sleep( SLEEP_SECONDS )
        self.LOG_PATH = os.environ['BDPY3_TEST__LOG_PATH']  # if None  ...outputs to console
        bd = BorrowDirect( {'LOG_PATH': self.LOG_PATH} )
        self.patron_barcode = os.environ['BDPY3_TEST__PATRON_BARCODE']
        self.api_url_root = os.environ['BDPY3_TEST__API_URL_ROOT']
        self.api_key = os.environ['BDPY3_TEST__API_KEY']
        self.university_code = os.environ['BDPY3_TEST__UNIVERSITY_CODE']
        self.partnership_id = os.environ['BDPY3_TEST__PARTNERSHIP_ID']

    def test_authenticate(self):
        """ Tests getting an authentication-id. """
        a = Authenticator()
        authentication_id = a.authenticate(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code )
        self.assertEqual(
            27, len(authentication_id) )

    def test_authorize(self):
        """ Tests authz session-extender. """
        a = Authenticator()
        authentication_id = a.authenticate(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code )
        time.sleep( SLEEP_SECONDS )
        validity = a.authorize(
            self.api_url_root, authentication_id )
        self.assertEqual(
            True, validity )

    ## end class AuthenticatorTests


class SearcherTests( unittest.TestCase ):

    def setUp(self):
        time.sleep( SLEEP_SECONDS )
        self.LOG_PATH = os.environ['BDPY3_TEST__LOG_PATH']  # if None  ...outputs to console
        bd = BorrowDirect( {'LOG_PATH': self.LOG_PATH} )
        self.patron_barcode = os.environ['BDPY3_TEST__PATRON_BARCODE']
        self.api_url_root = os.environ['BDPY3_TEST__API_URL_ROOT']
        self.api_key = os.environ['BDPY3_TEST__API_KEY']
        self.university_code = os.environ['BDPY3_TEST__UNIVERSITY_CODE']
        self.partnership_id = os.environ['BDPY3_TEST__PARTNERSHIP_ID']
        self.isbn_found_and_available = os.environ['BDPY3_TEST__ISBN_FOUND_AND_AVAILABLE']
        self.isbn_found_and_unavailable = os.environ['BDPY3_TEST__ISBN_FOUND_AND_UNAVAILABLE']
        self.isbn_not_found = os.environ['BDPY3_TEST__ISBN_NOT_FOUND']
        # self.isbn_available_locally = os.environ['BDPY3_TEST__ISBN_AVAILABLE_LOCALLY']  # TODO

    def test_search_bib_item_found_available(self):
        """ Tests bib item search for available found item.
            See README for example full-json response. """
        s = Searcher()
        ( title, author, year ) = ( 'Zen and the art of motorcycle maintenance - an inquiry into values', ['Pirsig, Robert M'], '1974' )
        result_dct = s.search_bib_item(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code, title, author, year )
        self.assertEqual(
            ['Available', 'OrigNumberOfRecords', 'PickupLocation', 'RequestLink'], sorted(result_dct.keys()) )
        self.assertEqual(
            True, result_dct['Available'] )

    def test_search_exact_item_found_available(self):
        """ Tests basic isbn search for available found item. """
        s = Searcher()
        ( search_key, search_value ) = ( 'ISBN', self.isbn_found_and_available )
        result_dct = s.search_exact_item(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code, search_key, search_value )
        self.assertEqual(
            ['Available', 'OrigNumberOfRecords', 'PickupLocation', 'RequestLink'], sorted(result_dct.keys()) )
        self.assertEqual(
            True, result_dct['Available'] )

    def test_search_exact_item_found_unavailable(self):
        """ Tests basic isbn search for unavailable found item. """
        s = Searcher()
        ( search_key, search_value ) = ( 'ISBN', self.isbn_found_and_unavailable )
        result_dct = s.search_exact_item(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code, search_key, search_value )
        self.assertEqual(
            ['Available', 'OrigNumberOfRecords', 'RequestLink'], sorted(result_dct.keys()) )
        self.assertEqual(
            False, result_dct['Available'] )

    def test_search_exact_item_not_found(self):
        """ Tests basic isbn search for not-found item. """
        s = Searcher()
        ( search_key, search_value ) = ( 'ISBN', self.isbn_not_found )
        result_dct = s.search_exact_item(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code, search_key, search_value )
        self.assertEqual(
            {"Problem":{"ErrorCode":"PUBFI002","ErrorMessage":"No result"}}, result_dct )

    ## TODO
    # def test_search_exact_item_available_locally(self):
    #     """ Tests basic isbn search for item that is available locally. """
    #     s = Searcher()
    #     ( search_key, search_value ) = ( 'ISBN', self.isbn_available_locally )
    #     result_dct = s.search(
    #         self.patron_barcode, search_key, search_value, self.api_url_root, self.api_key, self.partnership_id, self.university_code )
    #     self.assertEqual(
    #         {"Problem":{"ErrorCode":"PUBFI002","ErrorMessage":"No result"}}, result_dct )

    ## end class SearcherTests


class RequesterTests( unittest.TestCase ):

    def setUp(self):
        time.sleep( SLEEP_SECONDS )
        self.LOG_PATH = os.environ['BDPY3_TEST__LOG_PATH']  # if None  ...outputs to console
        bd = BorrowDirect( {'LOG_PATH': self.LOG_PATH} )
        self.patron_barcode = os.environ['BDPY3_TEST__PATRON_BARCODE']
        self.api_url_root = os.environ['BDPY3_TEST__API_URL_ROOT']
        self.api_key = os.environ['BDPY3_TEST__API_KEY']
        self.university_code = os.environ['BDPY3_TEST__UNIVERSITY_CODE']
        self.partnership_id = os.environ['BDPY3_TEST__PARTNERSHIP_ID']
        self.pickup_location = os.environ['BDPY3_TEST__PICKUP_LOCATION']
        self.isbn_found_and_available = os.environ['BDPY3_TEST__ISBN_FOUND_AND_AVAILABLE']
        self.isbn_found_and_unavailable = os.environ['BDPY3_TEST__ISBN_FOUND_AND_UNAVAILABLE']
        self.isbn_not_found = os.environ['BDPY3_TEST__ISBN_NOT_FOUND']

    # def test_request_item_found_and_available(self):
    #     """ Tests basic isbn request for available found item.
    #         NOTE: commented out because this will really request the item. """
    #     r = Requester()
    #     ( search_key, search_value ) = ( 'ISBN', self.isbn_found_and_available )
    #     result_dct = r.request_exact_item(
    #         self.patron_barcode, search_key, search_value, self.pickup_location, self.api_url_root, self.api_key, self.partnership_id, self.university_code )
    #     self.assertEqual(
    #         ['RequestNumber'], sorted(result_dct.keys()) )
    #     self.assertEqual(
    #         'BRO-', result_dct['RequestNumber'][0:4] )

    def test_request_item_not_found(self):
        """ Tests basic isbn request for not-found item.
            NOTE: will really attempt a request. """
        r = Requester()
        ( search_key, search_value ) = ( 'ISBN', self.isbn_not_found )
        result_dct = r.request_exact_item(
            self.patron_barcode, self.api_url_root, self.api_key, self.partnership_id, self.university_code, self.pickup_location, search_key, search_value )
        self.assertEqual(
            {'Problem': {'ErrorCode': 'PUBRI003', 'ErrorMessage': 'No result'}}, result_dct )

    def test_build_exact_search_params( self ):
        """ Tests for all expected isbn-search params. """
        r = Requester()
        ( partnership_id, pickup_location, search_key, search_value ) = ( 'a', 'b', 'c', 'd' )
        params = r.build_exact_search_params( partnership_id, pickup_location, search_key, search_value )
        self.assertEqual(
            ['ExactSearch', 'Notes', 'PartnershipId', 'PickupLocation'],
            sorted(params.keys()) )

    def test_build_bib_search_params( self ):
        """ Tests for all expected bib-search params. """
        r = Requester()
        ( partnership_id, pickup_location, title, author, year ) = ( 'a', 'b', 'c', 'd', 'e' )
        params = r.build_bib_search_params( partnership_id, pickup_location, title, author, year )
        self.assertEqual(
            ['BibSearch', 'PartnershipId', 'PickupLocation', 'ResultFilter'],
            sorted(params.keys()) )

    ## end class RequesterTests


if __name__ == '__main__':
  unittest.main()
