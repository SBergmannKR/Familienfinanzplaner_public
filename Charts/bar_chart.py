import matplotlib.pyplot as plt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget
)
import matplotlib.cm as cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibBarGraph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def plot_bar_from_dataframe(self, df, label):
        self.ax.clear()
        
        # Extract the 'month' and 'sum' columns
        xdata = df['Month'].dt.to_timestamp().dt.strftime('%Y-%m')
        heightdata = df['Sum']
        
        viridis = cm.get_cmap("viridis", 256)
        first_color = viridis(0)

        # Create the bar graph
        bar = self.ax.bar(xdata, heightdata, width=0.6, color=first_color)
        self.ax.set_title(label)

        # Rotate x-tick labels
        num_rows = len(df)
        # Rotate x-tick labels and set visibility based on the number of rows
        for index, tick in enumerate(self.ax.get_xticklabels()):
            tick.set_rotation(45)
            if num_rows > 10 and index % 2 == 0:  # Change 10 to the threshold you want
                tick.set_visible(False)
        self.ax.axhline(0, color='black', linewidth=0.8)
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        self.draw()