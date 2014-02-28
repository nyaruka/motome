from django.core.urlresolvers import reverse
from motome.tests import MotomeTestCase

class DashboardTest(MotomeTestCase):

    def test_dashboard(self):
        # get our dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, "%s?next=/dash/" % reverse('users.user_login'))
        self.login(self.admin)

        response = self.client.get(reverse('dashboard'))
        context = response.context


