import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree.common import safe_json

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

class BeginWaitPage(WaitPage):
    wait_for_all_groups = True
    template_name = 'Table/BeginWaitPage.html'

    def is_displayed(self):
        return self.round_number == 1

class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.colors = self.player.set_colors()
        self.player.labeling()
    

class ControlQuest(Page):
    form_model = models.Player
    form_fields = ['control_question1','control_question2', 'control_question3', 
    'control_question4', 'control_question5']
    def is_displayed(self):
        return self.round_number == 1

class ControlAnsw(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.cost_of_clicks = self.player.define_cost()

class Proberunde(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        round_without = self.round_number - 1
        return {'cost_clicks': self.player.cost_of_clicks,
                'round': round_without,
                'one': self.round_number,
        }

    def before_next_page(self):
        self.player.cost_of_clicks = self.player.define_cost()

class Halfway(Page):
    def is_displayed(self):
        return self.round_number == 12
    def before_next_page(self):
            self.player.cost_of_clicks = self.player.define_cost()

class ChangeCosts(Page):
    def is_displayed(self):
        return self.round_number == 12

    def vars_for_template(self):
        round_without = self.round_number - 1
        return {'cost_clicks': self.player.cost_of_clicks,
                'round': round_without,
                'one': self.round_number,
        }

class Filters(Page):
    form_model = models.Player
    form_fields = ['filters_applied']

    def vars_for_template(self):
        round_without = self.round_number - 1
        return {'round': round_without}

    def before_next_page(self):
        self.player.lst_strings = self.player.create_list()
        returns = self.player.lets_filter(self.player.lst_strings)
        self.player.selec_for_template = returns[2]
        self.player.lst_for_template = returns[0]
        self.player.filt_for_template = returns[1]
        self.player.price = self.player.set_price()
        self.player.cost_of_clicks = self.player.define_cost()

class Table(Page):
    form_model = models.Player
    form_fields = ['tempo', 'clicchi', 'clicchinuovi','distanza','arr_distanza','money_kept']

    def vars_for_template(self):
        round_without = self.round_number - 1
        return {'filters': self.player.filters_applied,
                'data': self.player.lst_for_template,
                'selected': self.player.selec_for_template,
                'dictionary': self.player.filt_for_template,
                'price' : self.player.price,
                'cost_clicks': self.player.cost_of_clicks,
                'round': round_without,
                'one': self.round_number,
        }

    def send_command(request):
        output = subprocess.check_output('ls', shell=True)
        print(output)
        return render(request, 'Table.html')


    def before_next_page(self):
        pay = self.player.set_payoffs(self.player.cost_of_clicks, self.player.price)
        self.player.payoff = pay[0]
        self.player.fake_payoff = pay[1]

class Results(Page):
    def vars_for_template(self):
        round_without = self.round_number - 1
        return {
            'earn': self.player.fake_payoff,
            'one': self.round_number,
            'round': round_without,
        }

    def before_next_page(self):
        self.player.lst_strings = ""
        self.player.filt_for_template = ""
        self.player.lst_for_template = ""
        self.player.selec_for_template = ""
        self.player.cost_of_clicks = self.player.define_cost()

class FinalResult(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        return {
            'total_payoff': sum([p.payoff for p in self.player.in_all_rounds()]),
            'paying_round_1': self.session.vars['paying_round_1'],
            'paying_round_2': self.session.vars['paying_round_2'],
            'pay1': self.player.in_round(self.session.vars['paying_round_1']).payoff,
            'pay2': self.player.in_round(self.session.vars['paying_round_2']).payoff,
            'payoff_plus' : self.participant.payoff_plus_participation_fee(),

        }

class Demographics(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    form_model = models.Player
    form_fields = ['q_age', 'q_gender','q_shopping','q_amazon','q_internet', 'q_risk1', 'q_risk2', 'q_motive1',
    'q_motive2','q_motive3','comments']

page_sequence = [
    Introduction,
    BeginWaitPage,
    Instructions,
    ControlQuest,
    ControlAnsw,
    Proberunde,
    Halfway,
    ChangeCosts,
    Filters,
    Table,
    Results,
    Demographics,
    FinalResult
]
