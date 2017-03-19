import datetime
import untangle

from .models import Account, Transaction


class Importer:

    def __init__(self, profile, filename):
        self.profile = profile
        self.filename = filename
        self.obj = untangle.parse(filename)
        self.ofx = self.obj.OFX

    @property
    def transactions(self):
        try:
            return self.ofx.CREDITCARDMSGSRSV1.CCSTMTTRNRS.CCSTMTRS.BANKTRANLIST.STMTTRN
        except IndexError:
            return self.ofx.BANKMSGSRSV1.STMTTRNRS.STMTRS.BANKTRANLIST.STMTTRN

    @property
    def account(self):
        try:
            account_data = self.ofx.CREDITCARDMSGSRSV1.CCSTMTTRNRS.CCSTMTRS.CCACCTFROM
            kind = 'CREDITCARD'
        except IndexError:
            account_data = self.ofx.BANKMSGSRSV1.STMTTRNRS.STMTRS.BANKACCTFROM
            kind = 'BANK'

        try:
            bank_id = account_data.BANKID.cdata
        except IndexError:
            bank_id = ''

        account_id = account_data.ACCTID.cdata

        account, created = Account.objects.update_or_create(
            profile=self.profile,
            bank_id=bank_id,
            account_id=account_id,
            defaults={'kind': kind}
        )

        return account

    def run(self):
        account = self.account

        for transaction in self.transactions:
            date_posted = datetime.datetime.strptime(
                transaction.DTPOSTED.cdata.split('.')[0], '%Y%m%d%H%M%S')

            fields = {
                'date_posted': date_posted,
                'amount': transaction.TRNAMT.cdata,
                'kind': transaction.TRNTYPE.cdata,
                'name': transaction.NAME.cdata,
            }

            Transaction.objects.update_or_create(
                account=account,
                profile=self.profile,
                transaction_id=transaction.FITID.cdata,
                defaults=fields,
            )
