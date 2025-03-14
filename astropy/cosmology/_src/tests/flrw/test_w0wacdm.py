# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Testing :mod:`astropy.cosmology.w0wacdm`."""

import numpy as np
import pytest

import astropy.units as u
from astropy.cosmology import Flatw0waCDM, Planck18, w0waCDM
from astropy.cosmology._src.parameter import Parameter
from astropy.cosmology._src.tests.test_core import ParameterTestMixin
from astropy.tests.helper import assert_quantity_allclose
from astropy.utils.compat.optional_deps import HAS_SCIPY

from .conftest import filter_keys_from_items
from .test_base import FlatFLRWMixinTest, FLRWTest
from .test_w0cdm import Parameterw0TestMixin

##############################################################################
# TESTS
##############################################################################


class ParameterwaTestMixin(ParameterTestMixin):
    """Tests for `astropy.cosmology.Parameter` wa on a Cosmology.

    wa is a descriptor, which are tested by mixin, here with ``TestFLRW``.
    These tests expect dicts ``_cls_args`` and ``cls_kwargs`` which give the
    args and kwargs for the cosmology class, respectively. See ``TestFLRW``.
    """

    def test_wa(self, cosmo_cls, cosmo):
        """Test Parameter ``wa``."""
        # on the class
        wa = cosmo_cls.parameters["wa"]
        assert isinstance(wa, Parameter)
        assert "Negative derivative" in wa.__doc__
        assert wa.unit is None
        assert wa.default == 0.0

        # on the instance
        assert cosmo.wa is cosmo.__dict__["wa"]
        assert cosmo.wa == self.cls_kwargs["wa"]

    def test_init_wa(self, cosmo_cls, ba):
        """Test initialization for values of ``wa``."""
        # test that it works with units
        ba.arguments["wa"] = ba.arguments["wa"] << u.one  # ensure units
        cosmo = cosmo_cls(*ba.args, **ba.kwargs)
        assert cosmo.wa == ba.arguments["wa"]

        # also without units
        ba.arguments["wa"] = ba.arguments["wa"].value  # strip units
        cosmo = cosmo_cls(*ba.args, **ba.kwargs)
        assert cosmo.wa == ba.arguments["wa"]

        # must be dimensionless
        ba.arguments["wa"] = 10 * u.km
        with pytest.raises(TypeError):
            cosmo_cls(*ba.args, **ba.kwargs)


class Testw0waCDM(FLRWTest, Parameterw0TestMixin, ParameterwaTestMixin):
    """Test :class:`astropy.cosmology.w0waCDM`."""

    def setup_class(self):
        """Setup for testing."""
        super().setup_class(self)
        self.cls = w0waCDM
        self.cls_kwargs.update(w0=-1, wa=-0.5)

    # ===============================================================
    # Method & Attribute Tests

    def test_clone_change_param(self, cosmo):
        """Test method ``.clone()`` changing a(many) Parameter(s)."""
        super().test_clone_change_param(cosmo)

        # `w` params
        c = cosmo.clone(w0=0.1, wa=0.2)
        assert c.w0 == 0.1
        assert c.wa == 0.2
        for n, v in filter_keys_from_items(c.parameters, ("w0", "wa")):
            v_expect = getattr(cosmo, n)
            assert_quantity_allclose(v, v_expect, atol=1e-4 * getattr(v, "unit", 1))

    # @pytest.mark.parametrize("z", valid_zs)  # TODO! recompute comparisons below
    def test_w(self, cosmo):
        """Test :meth:`astropy.cosmology.w0waCDM.w`."""
        # super().test_w(cosmo, z)

        assert u.allclose(cosmo.w(1.0), -1.25)
        assert u.allclose(
            cosmo.w([0.0, 0.5, 1.0, 1.5, 2.3]),
            [-1, -1.16666667, -1.25, -1.3, -1.34848485],
        )

    def test_repr(self, cosmo_cls, cosmo):
        """Test method ``.__repr__()``."""
        assert repr(cosmo) == (
            "w0waCDM(name='ABCMeta', H0=<Quantity 70. km / (Mpc s)>, Om0=0.27, "
            "Ode0=0.73, Tcmb0=<Quantity 3. K>, Neff=3.04, "
            "m_nu=<Quantity [0., 0., 0.] eV>, Ob0=0.03, w0=-1.0, wa=-0.5)"
        )

    # ===============================================================
    # Usage Tests

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy is not installed")
    @pytest.mark.parametrize(
        ("args", "kwargs", "expected"),
        [
            (  # no relativistic species
                (75.0, 0.3, 0.6),
                {"w0": -0.9, "wa": 0.1, "Tcmb0": 0.0},
                [2937.7807638, 4572.59950903, 5611.52821924, 6339.8549956] * u.Mpc,
            ),
            (  # massless neutrinos
                (75.0, 0.25, 0.5),
                {
                    "w0": -0.9,
                    "wa": 0.1,
                    "Tcmb0": 3.0,
                    "Neff": 3,
                    "m_nu": u.Quantity(0.0, u.eV),
                },
                [2907.34722624, 4539.01723198, 5593.51611281, 6342.3228444] * u.Mpc,
            ),
            (  # massive neutrinos
                (75.0, 0.25, 0.5),
                {
                    "w0": -0.9,
                    "wa": 0.1,
                    "Tcmb0": 3.0,
                    "Neff": 3,
                    "m_nu": u.Quantity(10.0, u.eV),
                },
                [2507.18336722, 3633.33231695, 4292.44746919, 4736.35404638] * u.Mpc,
            ),
        ],
    )
    def test_comoving_distance_example(self, cosmo_cls, args, kwargs, expected):
        """Test :meth:`astropy.cosmology.LambdaCDM.comoving_distance`.

        These do not come from external codes -- they are just internal checks to make
        sure nothing changes if we muck with the distance calculators.
        """
        super().test_comoving_distance_example(cosmo_cls, args, kwargs, expected)


# -----------------------------------------------------------------------------


class TestFlatw0waCDM(FlatFLRWMixinTest, Testw0waCDM):
    """Test :class:`astropy.cosmology.Flatw0waCDM`."""

    def setup_class(self):
        """Setup for testing."""
        super().setup_class(self)
        self.cls = Flatw0waCDM
        self.cls_kwargs.update(w0=-1, wa=-0.5)

    def test_repr(self, cosmo_cls, cosmo):
        """Test method ``.__repr__()``."""
        super().test_repr(cosmo_cls, cosmo)

        assert repr(cosmo) == (
            "Flatw0waCDM(name='ABCMeta', H0=<Quantity 70. km / (Mpc s)>, Om0=0.27, "
            "Tcmb0=<Quantity 3. K>, Neff=3.04, m_nu=<Quantity [0., 0., 0.] eV>, "
            "Ob0=0.03, w0=-1.0, wa=-0.5)"
        )

    # ===============================================================
    # Usage Tests

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy is not installed")
    @pytest.mark.parametrize(
        ("args", "kwargs", "expected"),
        [
            (  # no relativistic species
                (75.0, 0.25),
                {"w0": -0.95, "wa": 0.15, "Tcmb0": 0.0},
                [3123.29892781, 4956.15204302, 6128.15563818, 6948.26480378] * u.Mpc,
            ),
            (  # massless neutrinos
                (75.0, 0.25),
                {
                    "w0": -0.95,
                    "wa": 0.15,
                    "Tcmb0": 3.0,
                    "Neff": 3,
                    "m_nu": u.Quantity(0.0, u.eV),
                },
                [3122.92671907, 4955.03768936, 6126.25719576, 6945.61856513] * u.Mpc,
            ),
            (  # massive neutrinos
                (75.0, 0.25),
                {
                    "w0": -0.95,
                    "wa": 0.15,
                    "Tcmb0": 3.0,
                    "Neff": 3,
                    "m_nu": u.Quantity(10.0, u.eV),
                },
                [2337.70072701, 3372.13719963, 3988.6571093, 4409.35399673] * u.Mpc,
            ),
        ],
    )
    def test_comoving_distance_example(self, cosmo_cls, args, kwargs, expected):
        """Test :meth:`astropy.cosmology.LambdaCDM.comoving_distance`.

        These do not come from external codes -- they are just internal checks to make
        sure nothing changes if we muck with the distance calculators.
        """
        super().test_comoving_distance_example(cosmo_cls, args, kwargs, expected)


##############################################################################
# Comparison to Other Codes


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy.")
def test_varyde_lumdist_mathematica():
    """Tests a few varying dark energy EOS models against a Mathematica computation."""
    z = np.array([0.2, 0.4, 0.9, 1.2])

    # w0wa models
    cosmo = w0waCDM(H0=70, Om0=0.2, Ode0=0.8, w0=-1.1, wa=0.2, Tcmb0=0.0)
    assert u.allclose(
        cosmo.luminosity_distance(z),
        [1004.0, 2268.62, 6265.76, 9061.84] * u.Mpc,
        rtol=1e-4,
    )
    assert u.allclose(cosmo.de_density_scale(0.0), 1.0, rtol=1e-5)
    assert u.allclose(
        cosmo.de_density_scale([0.0, 0.5, 1.5]),
        [1.0, 0.9246310669529021, 0.9184087000251957],
    )

    cosmo = w0waCDM(H0=70, Om0=0.3, Ode0=0.7, w0=-0.9, wa=0.0, Tcmb0=0.0)
    assert u.allclose(
        cosmo.luminosity_distance(z),
        [971.667, 2141.67, 5685.96, 8107.41] * u.Mpc,
        rtol=1e-4,
    )

    cosmo = w0waCDM(H0=70, Om0=0.3, Ode0=0.7, w0=-0.9, wa=-0.5, Tcmb0=0.0)
    assert u.allclose(
        cosmo.luminosity_distance(z),
        [974.087, 2157.08, 5783.92, 8274.08] * u.Mpc,
        rtol=1e-4,
    )


##############################################################################
# Miscellaneous
# TODO: these should be better integrated into the new test framework


def test_equality():
    """Test equality and equivalence."""
    # mismatched signatures, both directions.
    newcosmo = w0waCDM(**Planck18.parameters, Ode0=0.6)
    assert newcosmo != Planck18
    assert Planck18 != newcosmo


@pytest.mark.skipif(not HAS_SCIPY, reason="test requires scipy")
def test_de_densityscale():
    cosmo = w0waCDM(H0=70, Om0=0.3, Ode0=0.70, w0=-1, wa=-0.5)

    z = np.array([0.1, 0.2, 0.5, 1.5, 2.5])
    assert u.allclose(
        cosmo.de_density_scale(z),
        [0.9934201, 0.9767912, 0.897450, 0.622236, 0.4458753],
        rtol=1e-4,
    )

    assert u.allclose(cosmo.de_density_scale(3), cosmo.de_density_scale(3.0), rtol=1e-7)
    assert u.allclose(
        cosmo.de_density_scale([1, 2, 3]),
        cosmo.de_density_scale([1.0, 2.0, 3.0]),
        rtol=1e-7,
    )
