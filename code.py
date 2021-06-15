from tkinter import *
from tkinter.ttk import Progressbar
from scraper.scraper import Scraper
from pandastable import Table, TableModel
import pandas as pd


class GUI:
    def __init__(self) -> None:
        self.window = Tk()
        # self.scraper = Scraper()
        self.window.geometry("500x400")
        self.window.minsize(500, 400)
        # self.window.maxsize(500,400)
        self.outerFrame = Frame(master=self.window)
        self.window.title("Amazon Product Scraper")
        self.mainFrame = Frame(self.outerFrame, bg="#F2A119")
        # Title
        # self.header = self.makeHeader(
        #     self.window, "Amazon Product Scraper", {"row": 0, "col": 0})

        # Directory row
        self.setLabel(self.mainFrame, "Directory", 10, {"row": 1, "col": 0})
        self.location = self.setEntry(self.mainFrame, 30, {"row": 1, "col": 1})

        # Product row
        self.setLabel(self.mainFrame, "Name of Product",
                      10, {"row": 2, "col": 0})
        self.URL = self.setEntry(self.mainFrame, 30, {"row": 2, "col": 1})

        # Max Items row
        self.setLabel(self.mainFrame, "Max Items", 10, {"row": 3, "col": 0})
        self.maxItems = self.setEntry(self.mainFrame, 30, {"row": 3, "col": 1})

        # Save Type row
        self.setLabel(self.mainFrame, "Save Type", 10, {"row": 4, "col": 0})
        self.typeSelect = self.makeRadio(self.mainFrame, {"row": 4, "col": 1})

        # Output File row
        self.setLabel(self.mainFrame, "Output File Name",
                      10, {"row": 5, "col": 0})
        self.fileName = self.setEntry(self.mainFrame, 30, {"row": 5, "col": 1})

        # Progress row
        self.setLabel(self.mainFrame, "Progress Status",
                      10, {"row": 6, "col": 0})
        # self.pb = self.createProgressBar(self.mainFrame, 250, {"row": 6, "col": 1})
        self.process = self.setEntry(self.mainFrame, 30, {"row": 6, "col": 1})

        # 8th row
        self.buttons = self.setButtons(self.mainFrame, ["Fetch!", "Exit"], {
            "row": 7, "col": 1}, self.onFetch)

        self.configureGrid(self.window)

        self.mainFrame.pack(fill=BOTH, expand=1, side=TOP)
        self.outerFrame.pack(expand=1)

    def onFetch(self):
        args = [self.location, self.URL, self.maxItems,
                self.typeSelect, self.fileName]
        url = "https://www.amazon.in/s?k="
        numbers = []
        for index in range(len(args)):
            value = args[index].get()
            if len(value) == 0:
                args[index].delete(0, END)
                args[index].insert(0, "ENter The Valid Value")

            if(index == 3 or index == 2):
                try:
                    numbers.append(int(args[index].get()))
                except:
                    args[index].delete(0, END)
                    args[index].insert(0, "Enter Interger Number")
        if(numbers[0] != -1 or numbers[1]):
            try:
                self.process .delete(0, END)
                self.process .insert(0, "Fetching.........")
                scraper = Scraper(args[0].get(
                ), url + args[1].get().replace(" ", "+"), numbers[0], numbers[1], args[4].get())
                dataFrame = scraper.amazonScrapper()
                self.showTable(dataFrame)
                self.process .delete(0, END)
                self.process .insert(0, "Fetching...... Completed!")
            except Exception as e:
                self.process.delete(0, END)
                self.process.insert(0, e)
        

    def setLabel(self, mainFrame, value, wd, position):
        labelDirectoryFrame = Frame(
            master=mainFrame,
            relief=RAISED,
            borderwidth=1,
        )
        labelDirectoryFrame.grid(
            row=position["row"], column=position["col"], padx=5, pady=5, sticky="nsew")
        # mainFrame.rowconfigure(labelDirectoryFrame, position["row"], weight=1)
        label = Label(master=labelDirectoryFrame, text=value, pady=10)
        label.pack()
        return label

    def setEntry(self, mainFrame, wd, position):
        labelDirectoryFrame = Frame(
            master=mainFrame,
            relief=RIDGE,
            borderwidth=5
        )
        labelDirectoryFrame.grid(
            row=position["row"], column=position["col"], padx=5, pady=5, sticky="nsew")
        entry = Entry(master=labelDirectoryFrame,
                      width=wd, borderwidth=5, relief=FLAT)
        entry.pack()
        return entry

    def setButtons(self, mainFrame, values, position, func):
        buttonsFrame = Frame(
            master=mainFrame,
            relief=FLAT,
            borderwidth=2,
            bg='orange'
        )
        buttonsFrame.grid(row=position["row"],
                          column=position["col"], padx=5, pady=5, sticky="nsew")
        fetchButton = Button(text="Fetch", master=buttonsFrame,
                             command=self.onFetch)
        fetchButton.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        exitButton = Button(text="Exit", master=buttonsFrame,
                            command=lambda: self.window.destroy())
        exitButton.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    def configureGrid(self, window):
        for row in range(window.grid_size()[0]+1):
            window.rowconfigure(row, weight=1, minsize=50)
            window.columnconfigure(row, weight=1, minsize=75)
        return

    def makeHeader(self, mainFrame, title, position):
        HeaderFrame = Frame(master=mainFrame)
        HeaderFrame.pack()
        Header = Label(text=title, master=HeaderFrame)
        Header.pack()
        return Header

    def makeRadio(self, mainFrame, position):
        select = StringVar(self.mainFrame, "1")
        ChoiceFrame = Frame(
            master=self.mainFrame,
            relief=SUNKEN,
            borderwidth=2
        )
        ChoiceFrame.grid(row=position["row"],
                         column=position["col"], padx=5, pady=5)
        choices = {
            "JSON": "1",
            "CSV": "2",
            "EXCEL": "3",
            "SQL": "4"
        }
        for (label, value) in choices.items():
            Radiobutton(master=ChoiceFrame, text=label, width=7, relief=FLAT, borderwidth=3,
                        value=value, indicator=0, variable=select, background="light blue").grid(row=0, column=int(value), sticky="ns")
        return select

    def createProgressBar(self, mainFrame, wd, position):
        pb = Progressbar(
            master=mainFrame,
            orient='horizontal',
            mode='indeterminate',
            length=wd, value=0
        )
        pb.grid(column=position["col"], row=position["row"], padx=10, pady=10)
        return pb

    def showTable(self, data):
        f = Frame(master=self.window)
        f.pack(fill=BOTH, expand=1)
        df = TableModel.getSampleData()
        pt = Table(f, dataframe=data,
                   showtoolbar=True, showstatusbar=True)
        pt.show()

    def start(self):
        self.window.mainloop()


if __name__ == "__main__":
    scraper = GUI()
    scraper.start()
