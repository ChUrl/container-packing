from typing import Dict, List, Tuple
import ezdxf
from ezdxf import colors
from ezdxf.addons import binpacking as bp
from ezdxf.addons.drawing import RenderContext, Frontend, matplotlib
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

# Length (cm), Width (cm), Height (cm), Capacity (kg)
CONTAINERS: List[Tuple[str, float, float, float, float]] = [
    ("20'", 590, 235, 239, 21670),
    ("40'", 1203, 240, 239, 25680),
    ("40'HQ", 1203, 235, 269, 26480),
]

COLORS: List[str] = ["red", "blue", "green", "yellow", "purple"]


def float_input(msg: str) -> float:
    read_str: str = input(f"{msg}: ")
    read_float: float

    try:
        read_float = float(read_str)
    except:
        return float_input(msg)

    return read_float


def int_input(msg: str) -> int:
    read_str: str = input(f"{msg}: ")
    read_int: int

    try:
        read_int = int(read_str)
    except:
        return int_input(msg)

    return read_int


def yes_no_input(msg: str) -> bool:
    read_str: str = input(f"{msg} (j/n): ").strip().lower()

    if read_str == "j":
        return True
    elif read_str == "n":
        return False
    else:
        return yes_no_input(msg)


def build_packer(
    items: List[Tuple[Tuple[float, float, float, float], int]]
) -> bp.Packer:
    packer: bp.Packer = bp.Packer()

    for i, ((length, width, height, weight), count) in enumerate(items):
        for ii in range(count):
            packer.add_item(f"Item {i}_{ii}", width, height, length, weight)

    return packer


def make_doc():
    doc = ezdxf.new()
    doc.layers.add("FRAME", color=colors.YELLOW)
    doc.layers.add("ITEMS")
    doc.layers.add("TEXT")
    return doc


def main() -> None:
    print("Container-Auslastungsrechner")
    items: List[Tuple[Tuple[float, float, float, float], int]] = []

    more_items: bool = True
    while more_items:
        print("\nNeues Packstück hinzufügen:")
        length = float_input("- Länge    (cm)")
        width = float_input("- Breite   (cm)")
        height = float_input("- Höhe     (cm)")
        weight = float_input("- Gewicht  (kg)")
        count = int_input("- Packstückzahl")

        items += [((length, width, height, weight), count)]

        more_items = yes_no_input("Weitere Packstücke hinzufügen?")

    for name, length, width, height, capacity in CONTAINERS:
        print(
            f"Teste {name:>5} Container ({length / 100:>5.2f}m x {width / 100:>5.2f}m x {height / 100:>5.2f}m mit {capacity / 1000:>5.2f}t)..."
        )

        packer: bp.Packer = build_packer(items)
        packer.add_bin(name, width, height, length, capacity)
        packer.pack(bp.PickStrategy.BIGGER_FIRST)

        if len(packer.unfitted_items) > 0:
            print(f"{name} Container ist zu klein!")
            break

        bins: List[bp.Bin] = []
        bins.extend(packer.bins)

        doc = make_doc()
        bp.export_dxf(doc.modelspace(), bins, offset=(0, 20, 0))
        # doc.saveas("packing.dxf")
        print(
            f"{name} Container passt: Zu {packer.get_fill_ratio() * 100:.2f}% gefüllt ({packer.get_total_weight():.2f}kg)"
        )

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Container bounding box
        ax.bar3d(0, 0, 0, length, width, height, alpha=0.1, color="gray")

        # Package bounding boxes
        for it in packer.bins[0].items:
            x, y, z = it.position
            w, h, l = it.width, it.height, it.depth
            ax.bar3d(x, y, z, l, w, h, color="red")

        plt.title(
            f"{name} Container mit {packer.get_fill_ratio() * 100:.2f}% Auslastung"
        )
        plt.autoscale()
        plt.show()

        return

    print("Konnte keinen passenden Container ermitteln!")


if __name__ == "__main__":
    main()
