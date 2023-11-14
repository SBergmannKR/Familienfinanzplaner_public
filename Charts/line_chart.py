import matplotlib.pyplot as plt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibLineGraph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_line_from_dataframe(self, df, label):
        self.ax.clear()
        
        # Extract the x and y data columns
        xdata = df['Buchungsdatum'].dt.strftime('%Y-%m')  # Adjust this as per your DataFrame
        ydata = df['Saldo']

        # Create the line graph
        self.ax.plot(xdata, ydata, color='blue', linewidth=2)

        self.ax.set_title(label)
        num_rows = len(df)
        for index, tick in enumerate(self.ax.get_xticklabels()):
            tick.set_rotation(45)
            if num_rows > 10 and index % 2 == 0:  # Change 10 to the threshold you want
                tick.set_visible(False)
        #self.ax.set_ylim(12500, 15000)

        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        self.draw()
