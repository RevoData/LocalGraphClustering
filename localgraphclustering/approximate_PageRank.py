from typing import *
import numpy as np
from .algorithms import acl_list
from .algorithms import fista_dinput_dense
from .cpp import aclpagerank_cpp
from .cpp import proxl1PRaccel
import warnings

def approximate_PageRank(G,
                         ref_nodes,
                         timeout: float = 100, 
                         iterations: int = 100000,
                         alpha: float = 0.15,
                         rho: float = 1.0e-6,
                         epsilon: float = 1.0e-2,
                         ys: Sequence[float] = None,
                         cpp: bool = True,
                         method: str = "acl"):
    """
    Computes PageRank vector locally.
    --------------------------------

    When method is "acl":

    Uses the Andersen Chung and Lang (ACL) Algorithm. For details please refer to: 
    R. Andersen, F. Chung and K. Lang. Local Graph Partitioning using PageRank Vectors
    link: http://www.cs.cmu.edu/afs/cs/user/glmiller/public/Scientific-Computing/F-11/RelatedWork/local_partitioning_full.pdf. 

    When method is "l1reg":

    Uses the Fast Iterative Soft Thresholding Algorithm (FISTA). This algorithm solves the l1-regularized
    personalized PageRank problem.

    The l1-regularized personalized PageRank problem is defined as

    min rho*||p||_1 + <c,p> + <p,Q*p>

    where p is the PageRank vector, ||p||_1 is the l1-norm of p, rho is the regularization parameter 
    of the l1-norm, c is the right hand side of the personalized PageRank linear system and Q is the 
    symmetrized personalized PageRank matrix.

    For details please refer to: 
    K. Fountoulakis, F. Roosta-Khorasani, J. Shun, X. Cheng and M. Mahoney. Variational 
    Perspective on Local Graph Clustering. arXiv:1602.01886, 2017.
    arXiv link:https://arxiv.org/abs/1602.01886

    Parameters
    ----------

    G: GraphLocal

    ref_nodes: Sequence[int]
        A sequence of reference nodes, i.e., nodes of interest around which
        we are looking for a target cluster.

    Parameters (optional)
    ---------------------

    alpha: float
        Default == 0.15
        Teleportation parameter of the personalized PageRank linear system.
        The smaller the more global the personalized PageRank vector is.
            
    rho: float
        Defaul == 1.0e-6
        Regularization parameter for the l1-norm of the model.
            
    iterations: int
        Default = 1000
        Maximum number of iterations of ACL algorithm.
                     
    timeout: float
        Default = 100
        Maximum time in seconds   

    method: string
        Default = 'acl'
        Which method to use.
        Options: 'l1reg', 'acl'.

    cpp: bool
        default = True
        Use the faster C++ version or not.

    Extra parameters for "l1reg" (optional)
    -------------------------------------------
            
    epsilon: float64
        Default == 1.0e-2
        Tolerance for FISTA for solving the l1-regularized personalized PageRank problem.

    ys: Sequence[float]
        Defaul == None
        Initial solutions for l1-regularized PageRank algorithm.
        If not provided then it is initialized to zero.
        This is only used for the C++ version of FISTA.

            
    Returns
    -------
        
    An np.ndarray (1D embedding) of the nodes.
    """ 

    if G._weighted:
        warnings.warn("The weights of the graph will be discarded. Use approximate_PageRank_weighted instead if you want to keep the edge weights.")

    if method == "acl":
        #print("Uses the Andersen Chung and Lang (ACL) Algorithm.")
        if ys != None:
            warnings.warn("\"acl\" doesn't support initial solutions, please use \"l1reg\" instead.")
        if cpp:
            n = G.adjacency_matrix.shape[0]
            (length,xids,values) = aclpagerank_cpp(n,np.uint32(G.adjacency_matrix.indptr),np.uint32(G.adjacency_matrix.indices),
                                               alpha,rho,ref_nodes,iterations,G.lib)
            p = np.zeros(n)
            p[xids] = values
            return p
        else:
            return acl_list(ref_nodes, G, alpha = alpha, rho = rho, max_iter = iterations, max_time = timeout)
    elif method == "l1reg":
        #print("Uses the Fast Iterative Soft Thresholding Algorithm (FISTA).")
        if cpp:
            if ys == None:
                return proxl1PRaccel(np.uint32(G.adjacency_matrix.indptr), np.uint32(G.adjacency_matrix.indices), 
                                     G.adjacency_matrix.data, ref_nodes, G.d, G.d_sqrt, G.dn_sqrt, G.lib, alpha = alpha, 
                                     rho = rho, epsilon = epsilon, maxiter = iterations, max_time = timeout)[2]            
            else:
                return proxl1PRaccel(np.uint32(G.adjacency_matrix.indptr) , np.uint32(G.adjacency_matrix.indices), 
                                     G.adjacency_matrix.data, ref_nodes, G.d, G.d_sqrt, G.dn_sqrt, ys, G.lib, alpha = alpha, 
                                     rho = rho, epsilon = epsilon, maxiter = iterations, max_time = timeout)[2]
        else:
            return fista_dinput_dense(ref_nodes, G, alpha = alpha, rho = rho, epsilon = epsilon, max_iter = iterations, max_time = timeout)
    else:
        raise Exception("Unknown method, available methods are \"acl\" or \"l1reg\".")
