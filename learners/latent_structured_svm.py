######################
# (c) 2012 Andreas Mueller <amueller@ais.uni-bonn.de>
# ALL RIGHTS RESERVED.
#
# DON'T USE WITHOUT AUTHOR CONSENT!
#

import numpy as np


from .ssvm import BaseSSVM
from .cutting_plane_ssvm import StructuredSVM
from .one_slack_ssvm import OneSlackSSVM
from .subgradient_ssvm import SubgradientStructuredSVM
from ..utils import find_constraint


class LatentSSVM(BaseSSVM):
    def __init__(self, problem, max_iter=100, C=1.0, verbose=1, n_jobs=1,
                 break_on_bad=True, show_loss_every=0, base_svm='n-slack',
                 check_constraints=True, batch_size=100, tol=0.0000001,
                 learning_rate=0.001, positive_constraint=None):
        self.base_svm = base_svm
        self.check_constraints = check_constraints
        self.break_on_bad = break_on_bad
        self.batch_size = batch_size
        self.tol = tol
        self.learning_rate = learning_rate
        
        self.positive_constraint=positive_constraint
        
        BaseSSVM.__init__(self, problem, max_iter, C, verbose=verbose,
                          n_jobs=n_jobs, show_loss_every=show_loss_every)

    def fit(self, X, Y, H_init=None):
        w = np.random.rand(self.problem.size_psi)
        if self.base_svm == 'n-slack':
            subsvm = StructuredSVM(
                self.problem, self.max_iter, self.C, self.check_constraints,
                verbose=self.verbose - 1, n_jobs=self.n_jobs,
                break_on_bad=self.break_on_bad, batch_size=self.batch_size,
                tol=self.tol)
        elif self.base_svm == '1-slack':
            subsvm = OneSlackSSVM(
                self.problem, self.max_iter, self.C, self.check_constraints,
                verbose=self.verbose - 1, n_jobs=self.n_jobs,
                break_on_bad=self.break_on_bad,positive_constraint=self.positive_constraint)
        elif self.base_svm == 'subgradient':
            subsvm = SubgradientStructuredSVM(
                self.problem, self.max_iter, self.C, verbose=self.verbose - 1,
                n_jobs=self.n_jobs, learning_rate=self.learning_rate)
        else:
            raise ValueError("base_svm must be one of '1-slack', 'n-slack', "
                             "'subgradient'. Got %s. " % str(self.base_svm))
        constraints = None
        ws = []
        if H_init is None:
            H_init = self.problem.init_latent(X, Y)
        self.H_init_ = H_init
        H = H_init
        
        for i in range(20):
            print 
        self.objective_curve_=[]
        for iteration in xrange(2):
            print("LATENT SVM ITERATION %d" % iteration)
            # find latent variables for ground truth:
            if iteration == 0:
                pass
            else:
                H_new = np.array([self.problem.latent(x, y, w)
                                  for x, y in zip(X, Y)])
                if np.all(H_new == H):
                    print("no changes in latent variables of ground truth."
                          " stopping.")
                    break
                print("changes in H: %d" % np.sum(H_new != H))

                # update constraints:
                if self.base_svm == 'n-slack':
                    constraints = [[] for i in xrange(len(X))]
                    for sample, h, i in zip(subsvm.constraints_, H_new,
                                            np.arange(len(X))):
                        for constraint in sample:
                            const = find_constraint(self.problem, X[i], h, w,
                                                    constraint[0])
                            y_hat, dpsi, _, loss = const
                            constraints[i].append([y_hat, dpsi, loss])
                H = H_new

            subsvm.fit(X, H, constraints=constraints)
            for i in range(20):
                print 

            #print subsvm.objective_curve_,constraints
            self.objective_curve_+=subsvm.objective_curve_
            
            
            
            print "finished iteration"
            w = subsvm.w
            ws.append(w)
            
#            if subsvm.objective_curve_==[]:
#                print "cannot get better"
#                break
            
#            if (iteration > 1 and self.objective_curve[-2] - self.objective_curve[-1] < self.tol):
#                print("objective converged.")
#                break

            
        self.w = w

    def predict(self, X):
        prediction = BaseSSVM.predict(self, X)
        return [self.problem.label_from_latent(h) for h in prediction]

    def predict_latent(self, X):
        return BaseSSVM.predict(self, X)
