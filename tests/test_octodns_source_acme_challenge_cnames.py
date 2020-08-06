from unittest import TestCase

from octodns.record import Record
from octodns.source.acme_challenge_cnames import ACMEChallengeCNAMESource
from octodns.zone import Zone


class TestACMEChallengeCNAMES(TestCase):

    def test_cnames(self):
        zone = Zone('unit.tests.', [])

        for record in [
            ('', {
                'ttl': 60,
                'type': 'A',
                'value': '1.2.3.4',
            }),
            ('', {
                'ttl': 60,
                'type': 'AAAA',
                'value': '2001:4860:4860::8888',
            }),
            ('quadA', {
                'ttl': 60,
                'type': 'AAAA',
                'value': '2001:4860:4860::8844',
            }),
            ('www', {
                'ttl': 60,
                'type': 'CNAME',
                'value': 'www.test.',
            }),
            ('text', {
                'ttl': 60,
                'type': 'TXT',
                'value': 'foobar',
            }),
            ('subdomain', {
                'ttl': 60,
                'type': 'NS',
                'value': 'ns.test.',
            })
        ]:
            zone.add_record(Record.new(zone, record[0], record[1]))

        expected = Zone('unit.tests.', [])

        for record in zone.records:
            expected.add_record(record)

        for record in [
            ('_acme-challenge', {
                'ttl': 60,
                'type': 'CNAME',
                'value': 'unit.tests.targetzone.test.',
            }),
            ('_acme-challenge.quadA', {
                'ttl': 60,
                'type': 'CNAME',
                'value': 'unit.tests.targetzone.test.',
            }),
            ('_acme-challenge.www', {
                'ttl': 60,
                'type': 'CNAME',
                'value': 'unit.tests.targetzone.test.',
            }),
        ]:
            expected.add_record(Record.new(expected, record[0], record[1]))

        source = ACMEChallengeCNAMESource('test', 'targetzone.test.', ttl=60)
        source.populate(zone)

        self.assertSetEqual(zone.records, expected.records)
