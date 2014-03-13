# -*- encoding: utf-8 -*-
################################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_osv


class test_journey(TransactionCase):

    def setUp(self):
        super(test_journey, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.partner_model = self.registry("res.partner")
        self.travel_model = self.registry("travel.travel")
        self.passenger_model = self.registry("travel.passenger")
        self.journey_model = self.registry("travel.journey")
        self.city_model = self.registry("res.better.zip")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        # Create values for test, travel and partner also created
        self.travel_id = self.travel_model.create(self.cr, self.uid, {
            'name': 'test_travel',
            'date_start': '2014-03-01',
            'date_stop': '2014-03-12',
        }, context=self.context)
        partner_id = self.partner_model.create(
            self.cr, self.uid, {'name': 'test_partner'}, context=self.context)
        self.passenger_id = self.passenger_model.create(self.cr, self.uid, {
            'partner_id': partner_id,
            'travel_id': self.travel_id,
        }, context=self.context)
        city_id = self.city_model.create(self.cr, self.uid, {
            'city': 'test_city'
        }, context=self.context)
        self.vals = {
            'origin': city_id,
            'destination': city_id,
            'departure': '2014-03-12',
            'passenger_id': self.passenger_id,
            'class_id': 1,
        }

    def test_create_journey(self):
        self.journey_model.create(
            self.cr, self.uid, self.vals, context=self.context)

    def test_create_journey_return(self):
        self.journey_model.create(
            self.cr, self.uid,
            dict(self.vals, is_return=True, return_departure='2014-03-31'),
            context=self.context)

    def test_import_journey(self):
        self.journey_model.create(
            self.cr, self.uid, self.vals, context=self.context)
        journey_import_model = self.registry("travel.journey.import")

        # Try with without a passenger_id
        wizard_bad = journey_import_model.create(self.cr, self.uid, {
            'travel_id': self.travel_id,
            'cur_passenger_id': self.passenger_id,
        }, context=self.context)
        self.assertRaises(
            except_osv,
            journey_import_model.data_import,
            self.cr, self.uid, [wizard_bad], context=self.context)

        # Try with with a passenger_id
        partner_id = self.partner_model.create(
            self.cr, self.uid, {'name': 'test_partner'}, context=self.context)
        import_passenger_id = self.passenger_model.create(self.cr, self.uid, {
            'partner_id': partner_id,
            'travel_id': self.travel_id,
        }, context=self.context)
        wizard_good = journey_import_model.create(self.cr, self.uid, {
            'travel_id': self.travel_id,
            'cur_passenger_id': self.passenger_id,
            'passenger_id': import_passenger_id,
        }, context=self.context)
        journey_import_model.data_import(
            self.cr, self.uid, [wizard_good], context=self.context)
