import matplotlib.pyplot as plt


class Container:
    def __init__(self, length, width, height, capacity):
        self.length = length  # Länge in m
        self.width = width  # Breite in m
        self.height = height  # Höhe in m
        self.capacity = capacity  # Gewichtskapazität in t
        self.items = []
        self.fitting = []

    def volume(self):
        return self.length * self.width * self.height

    def used_volume(self):
        if len(self.items) == 0:
            raise Exception("Container empty, can't calculate used volume!")

        return sum(item[0].volume() * item[1] for item in self.items)

    def utilization_volume(self):
        return self.used_volume() / self.volume() * 100

    def used_weight(self):
        if len(self.items) == 0:
            raise Exception("Container empty, can't calculate load weight!")

        return sum(item[0].weight * item[1] for item in self.items)

    def utilization_weight(self):
        return self.used_weight() / self.capacity * 100

    def try_fit(self, items) -> bool:
        self.items = items
        if self.used_weight() > self.capacity:
            print("Load too heavy!")
            return False
        if self.used_volume() > self.volume():
            print("Load too large!")
            return False

        fitting = []

        # Packstücke, Packordnung: Y, Z, X (Breite -> Höhe -> Länge)
        x_offset = 0
        y_offset = 0
        z_offset = 0
        for i, item_ in enumerate(items):
            item, count = item_

            for _ in range(count):
                fitting += [
                    (
                        x_offset,
                        y_offset,
                        z_offset,
                        item.length,
                        item.width,
                        item.height,
                        COLORS[i],
                    )
                ]

                if y_offset + item.width < self.width:
                    # Selbe "Zeile"
                    y_offset += item.width
                elif z_offset + item.height < self.height:
                    y_offset = 0
                    # Neue "Ebene" (Höhe)
                    z_offset += item.height
                elif x_offset + item.length < self.length:
                    y_offset = 0
                    z_offset = 0
                    # Neue "Scheibe" (Länge)
                    x_offset += item.length
                else:
                    return False

            if x_offset + item.length < self.length:
                x_offset += item.length
            else:
                return False
            y_offset = 0
            z_offset = 0

        self.fitting = fitting
        return True

    def visualize(self):
        if len(self.fitting) == 0:
            raise Exception("Container not fitted, can't visualize!")

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Container
        ax.bar3d(0, 0, 0, self.length, self.width, self.height, alpha=0.1, color="gray")

        # TODO: Don't add individual packages, combine them into blocks (perf)
        # Packages
        for x, y, z, l, w, h, color in self.fitting:
            ax.bar3d(x, y, z, l, w, h, color=color)

        ax.set_xlim([0, self.length])
        ax.set_ylim([0, self.width])
        ax.set_zlim([0, self.height])
        ax.set_xlabel("Länge (cm)")
        ax.set_ylabel("Breite (cm)")
        ax.set_zlabel("Höhe (cm)")
        plt.title(f"Container-Auslastung: {self.utilization_volume():.2f}%")
        plt.autoscale()
        plt.show()


class Item:
    def __init__(self, length, width, height, weight):
        self.length = length  # Länge in cm
        self.width = width  # Breite in cm
        self.height = height  # Höhe in cm
        self.weight = weight  # Gewicht in kg

    def volume(self):
        return self.length * self.width * self.height


# Length (cm), Width (cm), Height (cm), Capacity (kg)
CONTAINERS = {
    "20'": Container(590, 235, 239, 21670),
    "40'": Container(1203, 240, 239, 25680),
    "40'HQ": Container(1203, 235, 269, 26480),
}

COLORS = ["red", "blue", "green", "yellow", "purple"]


def main():
    print("Container-Auslastungsrechner")
    items = []

    while True:
        print("\nNeues Packstück hinzufügen:")
        length = float(input("Länge (cm): "))
        width = float(input("Breite (cm): "))
        height = float(input("Höhe (cm): "))
        weight = float(input("Gewicht (kg): "))
        count = int(input("Anzahl der Packstücke: "))

        item = Item(length, width, height, weight)
        items += [(item, count)]

        more_items = input("Weitere Packstücke hinzufügen? (ja/nein): ").strip().lower()
        if more_items != "ja":
            break

    for name, container in CONTAINERS.items():
        if container.try_fit(items):
            print(
                f"\nBenötigter Container: {name}, Gesamtauslastung (Volumen): {container.utilization_volume():.2f}%, Ladungsgewicht: {container.used_weight()}kg, Gesamtauslastung (Gewicht): {container.utilization_weight():.2f}%"
            )
            container.visualize()
            return

    print("Couldn't find fitting container!")


if __name__ == "__main__":
    main()
