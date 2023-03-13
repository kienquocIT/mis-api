from django.test import TestCase
from apps.sale.saledata.models.accounts import Salutation, Interest, AccountType, Industry, Contact
from apps.core.hr.models import Employee, Role, Group


# Create your tests here.
class MasterDataTest(TestCase):
    def test_create_salutation(self):
        """
        Create a salutation
        Returns: Object
        """
        obj = Salutation.object_normal.create(code='S000', title='Mr', description='Test Salutation')
        self.assertEqual(obj.code, "S000")
        self.assertEqual(obj.title, "Mr")
        self.assertEqual(obj.description, "Test Salutation")
        return obj

    def test_create_interest(self):
        """
        Create an interest
        Returns: Object
        """
        obj = Interest.object_normal.create(code='I000', title='Camping', description='Test Interest')
        self.assertEqual(obj.code, "I000")
        self.assertEqual(obj.title, "Camping")
        self.assertEqual(obj.description, "Test Interest")
        return obj

    def test_create_accountType(self):
        """
        Create an account type
        Returns: Object
        """
        obj = AccountType.object_normal.create(code='A000', title='Customer', description='Test Account Type')
        self.assertEqual(obj.code, "A000")
        self.assertEqual(obj.title, "Customer")
        self.assertEqual(obj.description, "Test Account Type")
        return obj

    def test_create_industry(self):
        """
        Create an industry
        Returns: Object
        """
        obj = Industry.object_normal.create(code='I000', title='IT Services', description='Test Industry')
        self.assertEqual(obj.code, "I000")
        self.assertEqual(obj.title, "IT Services")
        self.assertEqual(obj.description, "Test Industry")
        return obj


class ContactTest(TestCase):
    def test_create_contact(self):
        """
        Create a Contact
        Returns: Object
        """
        try:
            salutation = MasterDataTest.test_create_salutation(self)
        except Exception:
            print('Can not create Salutation')
            return

        try:
            interest = MasterDataTest.test_create_interest(self)
        except Exception:
            print('Can not create Interest')
            return

        try:
            employee = Employee.object_global.create(
                first_name='Nguyen Van',
                last_name='An',
                email='nguyenvanan@gmail.com',
                phone='0123456789',
            )
        except Exception:
            print('Can not create Employee')
            return

        contact = Contact.object_normal.create(
            owner=employee,
            bio='03/11/2001',
            salutation=salutation,
            fullname="Nguyen Thi Hong",
            phone='0987654321',
            mobile='0123456789',
            email='nguyenthihong@gmail.com',
            job_title='Manager',
            address_infor={"home_address": "Số 10/67, Xã Đức Lân, Huyện Mộ Đức, Quảng Ngãi", "work_address": "Số 22/20, Thị Trấn Bồng Sơn, Huyện Hoài Nhơn, Bình Định"},
            additional_infor={"tags": "tag", "gmail": "nth@gmail.com", "twitter": "nth.twitter", "facebook": "nth.facebook", "linkedln": "nth.linkedln", "interests": [interest.id]}
        )

        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
        self.assertEqual(contact.code, "I000")
