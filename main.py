import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Shadow, FancyArrowPatch
from matplotlib.bezier import BezierSegment

plt.rc("font", size=16)
plt.rc("font", family="Courier")
plt.rc("text", usetex=True)


SHADOW_DIR = -45
SHADOW_OFFSET = 0.085
SHADOW_COLOR = "gray"
DEFAULT_ARROW_STYLE = dict(
    arrowstyle="-|>,head_width=0.12,head_length=0.4",
    fc="k",
    ec="k",
    lw=1.25,
    shrinkA=4,
    shrinkB=1,
    mutation_scale=15,
)


def dir2d(angle):
    """Angle in degrees to a unit vector in 2D."""
    theta = np.radians(angle)
    return np.array([np.cos(theta), np.sin(theta)])


def draw_circle(xy, radius, with_shadow=True, **kwargs):
    """Draw a circle possibly with shadow."""
    c = Circle(xy, radius, **kwargs)
    plt.gca().add_patch(c)
    if with_shadow:
        offset = radius * dir2d(SHADOW_DIR) * SHADOW_OFFSET
        shadow = Shadow(c, *offset, fc=SHADOW_COLOR, ec="none", lw=0, zorder=-1)
        plt.gca().add_patch(shadow)


def create_arrow_patch(start, end, **kwargs):
    """Default arrow."""
    params = DEFAULT_ARROW_STYLE.copy()
    params.update(kwargs)
    color = kwargs.get("color", None)
    if color is not None:
        params["fc"] = color
        params["ec"] = color
    return FancyArrowPatch(start, end, **params)


class Node:

    xy: np.ndarray
    label: str = ""
    accept: bool = True
    radius: float = 1.0

    def __init__(self, xy, label="", accept=True, radius=1.0):
        self.xy = np.asarray(xy, dtype=float)
        self.label = label
        self.accept = accept
        self.radius = radius

    def draw(self, textonly=False, color="g", **kwargs):
        if not textonly:
            if not self.accept:
                draw_circle(self.xy, self.radius, fc=color, ec="k", lw=1)
            else:
                draw_circle(self.xy, self.radius, fc="w", ec="k", lw=1)
                draw_circle(self.xy, self.radius * 0.85, fc=color, ec="k", lw=1)

        if self.label:
            plt.text(*self.xy, self.label, ha="center", va="center", **kwargs)
        return self

    def arrowto(
        self,
        other,
        **kwargs,
    ):
        v = other.xy - self.xy
        angle = np.arctan2(v[1], v[0])
        start = self.xy + self.radius * dir2d(angle)
        end = other.xy - other.radius * dir2d(angle)
        patch = create_arrow_patch(start, end, **kwargs)
        plt.gca().add_patch(patch)

    def curvearrowto(
        self,
        other,
        angleA,
        angleB,
        **kwargs,
    ):
        start = self.xy + self.radius * dir2d(angleA)
        end = other.xy - other.radius * dir2d(angleB)
        patch = create_arrow_patch(start, end, **kwargs)
        patch.set_connectionstyle(f"angle3,angleA={angleA},angleB={angleB}")

        plt.gca().add_patch(patch)

    def loop(
        self,
        deg,
        **kwargs,
    ):
        angleA = deg - 10
        angleB = deg + 10
        start = self.xy + self.radius * dir2d(angleA)
        end = self.xy + self.radius * dir2d(angleB)
        if kwargs.get("connectionstyle") is None:
            kwargs["connectionstyle"] = (
                f"arc,angleA={angleA},angleB={angleB},armA=100,armB=100,rad=30"
            )
        patch = create_arrow_patch(start, end, **kwargs)
        plt.gca().add_patch(patch)


def example():
    plt.gca().set_aspect("equal", adjustable="box")
    plt.axis("off")

    start_text = Node((-0.7, 0), label="start", radius=0.15)
    start_text.draw(textonly=True, fontsize=10, weight="bold")

    q0 = Node((0, 0), label="$q_0$", radius=0.2)
    q1 = Node((1, 0), label="$q_1$", radius=0.2)
    q2 = Node((2, 0), label="$q_2$", radius=0.2)
    q3 = Node((3, 0), label="$q_3$", radius=0.2)

    start_text.arrowto(q0)
    q0.draw(color="r")
    for p, q in zip([q0, q1, q2], [q1, q2, q3]):
        q.draw()
        p.arrowto(q)

    for q in [q0, q1]:
        q.loop(90)

    q3.curvearrowto(q0, 250, 150, color="y")
    q1.curvearrowto(q2, -30, 30)
    q3.curvearrowto(q1, 225, 135)

    plt.gca().autoscale_view()
    plt.savefig("automata.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    example()
