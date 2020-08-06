import logging

from .base import BaseSource
from ..record import Record


class ACMEChallengeCNAMESource(BaseSource):
    SUPPORTS_GEO = False
    SUPPORTS_DYNAMIC = False
    SUPPORTS = set(('CNAME'))

    DEFAULT_TTL = 3600

    def __init__(self, id, target_zone, ttl=DEFAULT_TTL):
        self.log = logging.getLogger('{}[{}]'.format(
            self.__class__.__name__, id))
        self.log.debug('__init__: id=%s, target_zone=%s ttl=%s',
                       id, target_zone, ttl)

        if not target_zone.endswith('.'):
            target_zone += '.'

        self.target_zone = target_zone
        self.ttl = ttl
        super(ACMEChallengeCNAMESource, self).__init__(id)

    def populate(self, zone, target=False, lenient=False):
        self.log.debug('populate: name=%s, target=%s, lenient=%s', zone.name,
                       target, lenient)

        # build a list of records for which we can insert our CNAMEs
        #   include all A, AAAA, and CNAMEs except for wildcards
        eligible_records = [r for r in zone.records if
                            '*' not in r.name and
                            r._type in {"A", "AAAA", "CNAME"}]

        # insert our CNAMEs into the zone
        for record in eligible_records:
            if record.name == '':
                name = "_acme-challenge"
            else:
                name = "_acme-challenge." + record.name
            target = "_acme-challenge." + record.fqdn + self.target_zone
            data = {"type": "CNAME", "ttl": self.ttl, "value": target}
            acme_cname = Record.new(zone, name, data, source=self,
                                    lenient=lenient)
            zone.add_record(acme_cname, replace=True, lenient=lenient)
