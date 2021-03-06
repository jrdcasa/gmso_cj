"""A topology within a topology."""
import warnings

from boltons.setutils import IndexedSet

from gmso.core.atom import Atom
from gmso.core.topology import Topology


class SubTopology(object):
    """A sub-topology i.e. topology within a topology.

    This class provides a hierarchical topological representation to
    the topology as it imperative with many chemical structures to have
    separation of layers/ boundaries. A sub-topology can be added to a
    gmso.Topology object which will be the parent of the sub-topology.

    Parameters
    ----------
    name : str, optional, default='Sub-Topology'
        Name of the sub-topology
    parent : gmso.Topology, optional, default=None
        The parent topology of this SubTopology

    Attributes
    ----------
    sites : IndexedSet of gmso.Site objects
        Collection of sites within this sub-topology
    n_sites : int
        Number of sites withing this sub-topology
    """

    def __init__(self, name="Sub-Topology", parent=None):
        if name is not None:
            self._name = str(name)
        if parent is None:
            self._parent = parent
        else:
            self._parent = _validate_parent(parent)
        self._sites = IndexedSet()

    @property
    def name(self):
        """Return the name of the sub-topology."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of the sub-topology."""
        self._name = str(name)

    @property
    def sites(self):
        """Return the sites associated with the sub-topology."""
        return self._sites

    @property
    def n_sites(self):
        """Return the number of sites associated with the sub-topology."""
        return len(self.sites)

    @property
    def parent(self):
        """Return the parent of the sub-topology."""
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Set the parent of the sub-topology."""
        warnings.warn(
            "Setting a parent is potentially dangerous. Consider using "
            "Topology.add_subtopology instead"
        )
        if parent is None:
            raise NotImplementedError(
                "Setting parents to None is not yet supported"
            )
        self._parent = _validate_parent(parent)

    def add_site(self, site, update_types=True):
        """Add a site to this sub-topology.

        This method adds a site to the sub-topology.
        If the sub-topology has a parent, the site will
        also be added to the parent topology. If the
        update_types parameter is set to true (default
        behavior), this method will also check if there
        is an gmso.AtomType associated with the site and
        it to the sub-topology's AtomTypes collection.

        Parameters
        ----------
        site : gmso.Atom
            The site to be added to this sub-topology
        update_types : (bool), default=True
            If true, add this site's atom type to the sub-topology's set of AtomTypes

        Raises
        ------
        TypeError
            If the parameter site is not of type topology.Site
        """

        site = _validate_site_addability(site)
        if site in self.sites:
            warnings.warn("Redundantly adding Site {}".format(site))
        self._sites.add(site)
        if self.parent:
            self.parent.add_site(site, update_types=update_types)

    def __repr__(self):
        """Return a formatted representation of the sub-topology."""
        return (
            f"<SubTopology {self.name},\n "
            f"{self.n_sites} sites,\n "
            f"id: {id(self)}>"
        )

    def __str__(self):
        """Return a string representation of the sub-topology."""
        return (
            f"<SubTopology {self.name}, "
            f"{self.n_sites} sites, "
            f"id: {id(self)}>"
        )

    def json_dict(self):
        """Return a json serializable dictionary of this subtopology."""
        subtop_dict = {"name": self.name, "atoms": []}

        for site in self._sites:
            subtop_dict["atoms"].append(self.parent.get_index(site))

        return subtop_dict


def _validate_parent(parent):
    """Ensure the parent is a topology."""
    if isinstance(parent, Topology):
        return parent
    else:
        raise TypeError("Argument {} is not type Topology".format(parent))


def _validate_site_addability(site):
    """Ensure a site is a site and not already a part of a top/subtop."""
    if not isinstance(site, Atom):
        raise TypeError("Argument {} is not a Site. See gmso/core/atom.py")
    # TODO: Some sort of a check on site.parent
    return site
