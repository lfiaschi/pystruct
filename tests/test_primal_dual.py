#from crf import BinaryGridCRF
#from structured_svm import StructuredSVM, SubgradientStructuredSVM
#from structured_svm import objective_primal, PrimalDSStructuredSVM
#from toy_datasets import binary

#from IPython.core.debugger import Tracer
#tracer = Tracer()


#def test_primal_dual_binary():
    #for C in [1, 100, 100000]:
        #for dataset in binary:
            #X, Y = dataset(n_samples=1)
            #crf = BinaryGridCRF()
            #clf = StructuredSVM(problem=crf, max_iter=200, C=C, verbose=0,
                    #check_constraints=True)
            #clf.fit(X, Y)
            #clf2 = SubgradientStructuredSVM(problem=crf, max_iter=200, C=C,
                    #verbose=0)
            #clf2.fit(X, Y)
            #clf3 = PrimalDSStructuredSVM(problem=crf, max_iter=200, C=C,
                    #verbose=0)
            #clf3.fit(X, Y)
            #obj = objective_primal(crf, clf.w, X, Y, C)
            ## the dual finds the optimum so it might be better
            #obj2 = objective_primal(crf, clf2.w, X, Y, C)
            #obj3 = objective_primal(crf, clf3.w, X, Y, C)
            #assert(obj <= obj2)
            #assert(obj <= obj3)
            #print("objective difference: %f\n" % (obj2 - obj))
            #print("objective difference DS: %f\n" % (obj3 - obj))
#test_primal_dual_binary()
