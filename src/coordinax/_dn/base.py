"""Representation of coordinates in different systems."""

__all__ = ["AbstractNDVector", "AbstractNDVectorDifferential"]


from abc import abstractmethod
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import quaxed.lax as qlax
import quaxed.numpy as qnp

from coordinax._base import AbstractVectorBase
from coordinax._base_dif import AbstractVectorDifferential
from coordinax._base_vec import AbstractVector
from coordinax._utils import classproperty

if TYPE_CHECKING:
    from typing_extensions import Never


class AbstractNDVector(AbstractVector):
    """Abstract representation of N-D coordinates in different systems."""

    @classproperty
    @classmethod
    def _cartesian_cls(cls) -> type[AbstractVectorBase]:
        from .builtin import CartesianNDVector

        return CartesianNDVector

    @classproperty
    @classmethod
    @abstractmethod
    def differential_cls(cls) -> "Never":  # type: ignore[override]
        msg = "Not yet implemented"
        raise NotImplementedError(msg)

    # ===============================================================
    # Array API

    @property
    def mT(self) -> "Self":  # noqa: N802
        """Transpose the vector.

        The last axis is interpreted as the feature axis. The matrix
        transpose is performed on the last two non-feature axes.
        """
        ndim = self.q.ndim
        if ndim < 2:
            msg = (
                f"x must be at least two-dimensional for matrix_transpose; got {ndim=}"
            )
            raise ValueError(msg)
        axes = (*range(ndim - 2), ndim - 2, ndim - 3)
        return replace(self, q=qlax.transpose(self.q, axes))

    @property
    def shape(self) -> tuple[int, ...]:
        """Get the shape of the vector's components.

        When represented as a single array, the vector has an additional
        dimension at the end for the components.

        """
        return self.q.shape[:-1]

    @property
    def T(self) -> "Self":  # noqa: N802
        """Transpose the vector."""
        return replace(self, q=qlax.transpose(self.q, [*range(self.q.ndim)[1::-1], -1]))

    # ===============================================================
    # Further array methods

    def flatten(self) -> "Self":
        """Flatten the vector."""
        return replace(self, q=qnp.reshape(self.q, (self.size, self.q.shape[-1]), "C"))

    def reshape(self, *hape: Any, order: str = "C") -> "Self":
        """Reshape the vector."""
        return replace(self, q=self.q.reshape(*hape, self.q.shape[-1], order=order))


class AbstractNDVectorDifferential(AbstractVectorDifferential):
    """Abstract representation of N-D vector differentials."""

    @classproperty
    @classmethod
    def _cartesian_cls(cls) -> type[AbstractVectorBase]:
        from .builtin import CartesianDifferentialND

        return CartesianDifferentialND

    @classproperty
    @classmethod
    @abstractmethod
    def integral_cls(cls) -> type[AbstractNDVector]:
        raise NotImplementedError

    # ===============================================================
    # Array API

    @property
    def mT(self) -> "Self":  # noqa: N802
        """Transpose the vector.

        The last axis is interpreted as the feature axis. The matrix
        transpose is performed on the last two non-feature axes.
        """
        ndim = self.d_q.ndim
        if ndim < 2:
            msg = (
                f"x must be at least two-dimensional for matrix_transpose; got {ndim=}"
            )
            raise ValueError(msg)
        axes = (*range(ndim - 2), ndim - 2, ndim - 3)
        return replace(self, q=qlax.transpose(self.d_q, axes))

    @property
    def shape(self) -> tuple[int, ...]:
        """Get the shape of the vector's components.

        When represented as a single array, the vector has an additional
        dimension at the end for the components.

        """
        return self.d_q.shape[:-1]

    @property
    def T(self) -> "Self":  # noqa: N802
        """Transpose the vector."""
        return replace(
            self, q=qlax.transpose(self.d_q, [*range(self.d_q.ndim)[1::-1], -1])
        )

    # ===============================================================
    # Further array methods

    def flatten(self) -> "Self":
        """Flatten the vector."""
        return replace(
            self, q=qnp.reshape(self.d_q, (self.size, self.d_q.shape[-1]), "C")
        )

    def reshape(self, *hape: Any, order: str = "C") -> "Self":
        """Reshape the vector."""
        return replace(self, q=self.q.reshape(*hape, self.q.shape[-1], order=order))
