"""
The cluster model contains functions computing clustering using CobwebTrees and
their derivatives.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
import json
import re
import copy

def cluster_iter(tree, instances, minsplit=1, maxsplit=100000,  mod=True):
    """Categorize a list of instances into a tree and return an iterator over
    cluster labelings generated from successive splits of the tree.

    An inital clustering is derived by splitting the root node, then each
    subsequent clustering is based on splitting the least coupled cluster (in
    terms of category utility). The first clustering returned by the iterator is
    after a minsplit number of splits and the last one is after a maxsplit
    number of splits. This process may halt early if it reaches the case where
    there are no more clusters to split (each instance in its own cluster).
    Because splitting is a modifying operation, a deepcopy of the tree is made
    before creating the iterator.

    :param tree: A category tree to be used to generate clusters, it can be pre-trained or newly created.
    :param instances: A list of instances to cluster
    :param minsplit: The minimum number of splits to perform on the tree
    :param maxsplit: the maximum number of splits to perform on the tree
    :param mod: A flag to determine if instances will be fit (i.e. modifying knoweldge) or categorized (i.e. not modifiying knowledge)
    :type tree: :class:`CobwebTree <concept_formation.cobweb.CobwebTree>`, :class:`Cobweb3Tree <concept_formation.cobweb3.Cobweb3Tree>`, or :class:`TrestleTree <concept_formation.trestle.TrestleTree>`
    :type instances: [:ref:`Instance<instance-rep>`, :ref:`Instance<instance-rep>`, ...]
    :type minsplit: int
    :type maxsplit: int
    :type mod: bool
    :returns: an iterator of clusterings based on a number of splits between minsplit and maxsplit
    :rtype: iterator

    .. warning:: minsplit must be >=1 and maxsplit must be >= minsplit
    """
    if minsplit < 1: 
        raise ValueError("minsplit must be >= 1") 
    if minsplit > maxsplit: 
        raise ValueError("maxsplit must be >= minsplit")

    tree = copy.deepcopy(tree)

    if mod:
        temp_clusters = [tree.ifit(instance) for instance in instances]
    else:
        temp_clusters = [tree.categorize(instance) for instance in instances]
    
    for nth_split in range(1,maxsplit+1):

        if nth_split >= minsplit:
            clusters = []
            for i,c in enumerate(temp_clusters):
                while (c.parent and c.parent.parent):
                    c = c.parent
                clusters.append("Concept" + c.concept_id)
            yield clusters

        split_cus = sorted([(tree.root.cu_for_split(c) -
                             tree.root.category_utility(), i, c) for i,c in
                            enumerate(tree.root.children) if c.children])

        # Exit early, we don't need to re-reun the following part for the
        # last time through
        if not split_cus:
            break

        # Split the least cohesive cluster
        tree.root.split(split_cus[-1][2])

        nth_split+=1

def cluster(tree, instances, minsplit=1, maxsplit=1, mod=True):
    """Categorize a list of instances into a tree and return a list of
    flat cluster labelings based on successive splits of the tree.

    :param tree: A category tree to be used to generate clusters.
    :param instances: A list of instances to cluster
    :param minsplit: The minimum number of splits to perform on the tree
    :param maxsplit: the maximum number of splits to perform on the tree
    :param mod: A flag to determine if instances will be fit (i.e. modifying knoweldge) or categorized (i.e. not modifiying knowledge)
    :type tree: :class:`CobwebTree <concept_formation.cobweb.CobwebTree>`, :class:`Cobweb3Tree <concept_formation.cobweb3.Cobweb3Tree>`, or :class:`TrestleTree <concept_formation.trestle.TrestleTree>`
    :type instances: [:ref:`Instance<instance-rep>`, :ref:`Instance<instance-rep>`, ...]
    :type minsplit: int
    :type maxsplit: int
    :type mod: bool
    :returns: a list of lists of cluster labels based on successive splits between minsplit and maxsplit.
    :rtype: [[minsplit clustering], [minsplit+1 clustering], ... [maxsplit clustering]]

    .. seealso:: :meth:`cluster_iter`
    
    """
    return [c for c in cluster_iter(tree,instances,minsplit,maxsplit,mod)]

def k_cluster(tree,instances,k=3,mod=True):
    """Categorize a list of instances into a tree and return a flat cluster
    where ``len(set(clustering)) <= k``. 

    Clusterings are generated by successively splitting the tree until a split
    results in a clustering with > k clusters at which point the clustering just
    before that split is returned. It is possible for this process to return a
    clustering with < k clusters.

    :param tree: A category tree to be used to generate clusters, it can be pre-trained or newly created.
    :param instances: A list of instances to cluster
    :param k: A desired number of clusters to generate
    :param mod: A flag to determine if instances will be fit (i.e. modifying knoweldge) or categorized (i.e. not modifiying knowledge)
    :type tree: :class:`CobwebTree <concept_formation.cobweb.CobwebTree>`, :class:`Cobweb3Tree <concept_formation.cobweb3.Cobweb3Tree>`, or :class:`TrestleTree <concept_formation.trestle.TrestleTree>`
    :type instances: [:ref:`Instance<instance-rep>`, :ref:`Instance<instance-rep>`, ...]
    :type k: int
    :type mod: bool
    :returns: a flat cluster labeling
    :rtype: [label1, label2, ...]

    .. seealso:: :meth:`cluster_iter`
    .. warning:: k must be >= 2.
    """

    if k < 2:
        raise ValueError("k must be >=2, all nodes in Cobweb are guaranteed to have at least 2 children.")

    clustering = ["Concept" + tree.root.concept_id for i in instances]
    for c in cluster_iter(tree, instances,mod=mod):
        if len(set(c)) > k:
            break
        clustering = c

    return clustering

def depth_labels(tree,instances,mod=True):
    """Categorize a list of instances into a tree and return a list of lists of
    labelings for  each instance based on different depth cuts of the tree.

    The returned matrix is max(conceptDepth) X len(instances). Labelings are
    ordered general to specific with final_labels[0] being the root and
    final_labels[-1] being the leaves.

    :param tree: A category tree to be used to generate clusters, it can be pre-trained or newly created.
    :param instances: A list of instances to cluster
    :param mod: A flag to determine if instances will be fit (i.e. modifying knoweldge) or categorized (i.e. not modifiying knowledge)
    :type tree: :class:`CobwebTree <concept_formation.cobweb.CobwebTree>`, :class:`Cobweb3Tree <concept_formation.cobweb3.Cobweb3Tree>`, or :class:`TrestleTree <concept_formation.trestle.TrestleTree>`
    :type instances: [:ref:`Instance<instance-rep>`, :ref:`Instance<instance-rep>`, ...]
    :type mod: bool
    :returns: a list of lists of cluster labels based on each depth cut of the tree
    :rtype: [[root labeling], [depth1 labeling], ... [maxdepth labeling]]
    """
    if mod:
        temp_labels = [tree.ifit(instance) for instance in instances]
    else:
        temp_labels = [tree.categorize(instance) for instance in instances]

    instance_labels = []
    max_depth = 0
    for t in temp_labels:
        labs = []
        depth = 0
        label = t
        while label.parent:
            labs.append("Concept" + label.concept_id)
            depth += 1
            label = label.parent
        labs.append("Concept" + label.concept_id)
        depth += 1
        instance_labels.append(labs)
        if depth > max_depth:
            max_depth = depth

    for f in instance_labels:
        f.reverse()
        last_label = f[-1]
        while len(f) < max_depth:
            f.append(last_label)

    final_labels = []
    for d in range(len(instance_labels[0])):
        depth_n = []
        for i in instance_labels:
            depth_n.append(i[d])
        final_labels.append(depth_n)

    return final_labels
