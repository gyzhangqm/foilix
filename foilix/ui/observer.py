#!/usr/bin/python
# coding: utf-8

r"""Observer pattern"""

import abc


class Observable(object):
    r"""Base class for objects that can be observed"""
    def __init__(self):
        self.observers = list()

    def add_observers(self, o):
        r"""Add an observer

        Parameters
        ----------
        o : subclass of Observer

        """
        # assert isinstance(o, Observer)
        if not isinstance(o, Observer):
            msg = "Cannot add an observer that is not an instance of Observer"
            raise ValueError(msg)
        self.observers.append(o)

    def notify_observers(self,
                         message,
                         n,
                         i_par,
                         pts,
                         score,
                         foil_parameterization_type):
        r"""Notify the observers registered in self.observers by calling their
        update() function

        Parameters
        ----------
        message : str
            Message explaining the reason for update
        n : int
            Iteration number
        i_par : int
            Particle id
        pts : array
            The values of the vector for the particle
        score : float
            The score
        foil_parameterization_type : str

        """
        for l in self.observers:
            l.update(message, n, i_par, pts, score, foil_parameterization_type)


class Observer(object):
    r"""Abstract base class for observers"""
    # __metaclass__ = abc.ABCMeta

    # @abc.abstractmethod
    def update(self, message, n, i_par, pts, score, foil_parameterization_type):
        r"""The method Observers must implement in order to be updated

        Parameters
        ----------
        message : str
            Message explaining the reason for update
        n : int
            Iteration number
        i_par : int
            Particle id
        pts : array
            The values of the vector for the particle
        score : float
            The score
        foil_parameterization_type : str
            PARSEC, SYM_PARSEC, NURBS or SYM_NURBS

        """
        raise NotImplementedError
