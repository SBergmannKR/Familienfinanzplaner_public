import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.cm as cm

class PieChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_pie(self, df, label):
        self.ax.clear()
        self.ax.set_title(label)
        # Generate the Viridis colormap
        viridis = cm.get_cmap("viridis", len(df['Betrag']))
        self.ax.pie(df['Betrag'], labels=df['Kategorie'], autopct='%1.1f%%', startangle=90, colors=viridis(range(len(df['Betrag']))))
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        self.draw()