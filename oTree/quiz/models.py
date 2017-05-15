from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import csv
import operator

author = 'Your name here'

doc = """
A quiz app that reads its questions from a spreadsheet
(see quiz.csv in this directory).
There is 1 question per page; the number of pages in the game
is determined by the number of questions in the CSV.
See the comment below about how to randomize the order of pages.
"""


class Constants(BaseConstants):
    name_in_url = 'quiz'
    players_per_group = None

    with open('quiz/quiz.csv') as f:
        questions = list(csv.DictReader(f))

    num_rounds = len(questions)
    options = [('A',''), ('B', '')]


class Subsession(BaseSubsession):
    sorted_d = models.CharField()
    percentile = models.CharField()
    participants = models.PositiveIntegerField()
    
    def before_session_starts(self):
        self.group_randomly()
        if self.round_number == 1:
            self.session.vars['questions'] = Constants.questions    #Qui si assegnano le questions dal CSV al session.vars
            ## ALTERNATIVE DESIGN:
            ## to randomize the order of the questions, you could instead do:

            # import random
            # randomized_questions = random.sample(Constants.questions, len(Constants.questions))
            # self.session.vars['questions'] = randomized_questions

            ## and to randomize differently for each participant, you could use
            ## the random.sample technique, but assign into participant.vars
            ## instead of session.vars.

        for p in self.get_players():                    #crea un pool per ogni round essenzialmente, da questo estrapola id, question e solution
            question_data = p.current_question()        #le choice vengono chiamate in views allo stesso modo
            p.question_id = question_data['id']
            p.question = question_data['question']
            p.solution = question_data['solution']

        self.participants = len(self.get_players())

    def get_ranking(self):                               #this function should get the results from all participants, rank them and then get the quantile
        d = dict()                                              #PROBLEMS: get the count in dictionary
        for p in self.get_players():
            d[p] = p.cum_count
        self.sorted_d = sorted(d.items(), key=operator.itemgetter(1))

    def assign_percentile(self):
        self.percentile = []
        for i in range(0, self.participants):
            perci = (i+1)/self.participants
            self.percentile.append(perci)
        
    def player_perc(self):
        for p in self.get_players():
            for i in range(0, self.participants):
                if p == self.sorted_d[i][0]:
                    p.perc = self.percentile[i]
                    p.participant.vars['perc'] = p.perc

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    question_id = models.PositiveIntegerField()
    question = models.CharField()
    solution = models.CharField()
    submitted_answer = models.CharField(widget=widgets.RadioSelect())
    is_correct = models.BooleanField()
    count = models.PositiveIntegerField()
    cum_count = models.PositiveIntegerField()
    perc = models.FloatField()
    
    def current_question(self):
        return self.session.vars['questions'][self.round_number - 1] #Questo essenzialmente chiama un set di domande, il quale verrà poi 
                                                                     #rinominato question_data. Il -1 è perché il primo elemento è chiaramente 0!

    def check_correct(self):
        self.is_correct = self.submitted_answer == self.solution
    

    def count_correct(self):
        self.count = 0
        if self.is_correct:
            self.count = 1
    ### ADJUST HERE ###
    for elem in q_confidence_list:
        elem = models.CharField(initial=None, choices = Constants.options, widget=widgets.RadioSelectHorizontal())

    