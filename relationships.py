"""
TODO: visual interface with a table where you can check cells off to indicate presence of a relationship (or uncheck to indicate lack of)
TODO: make nodes dragable
"""

import networkx as nx
import matplotlib.pyplot as plt
import csv
import math

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import os

class Node:
    # ===Constructor===
    def __init__(self, name, peopleDict, posList=None, negList=None, workList=None):
        self.name = name
        self.posList = posList or []
        self.negList = negList or []
        self.workList = workList or []
        self.peopleDict = peopleDict
    
    # ===Adding relationship===
    # addPos(rel : Node list)
    def addPos(self, rel):
        for i in rel:
            self.peopleDict.ensurePerson(i)
            if self.posList.count(i) == 0:
                self.posList.append(i)

    def addNeg(self, rel):
        for i in rel:
            self.peopleDict.ensurePerson(i)
            if self.negList.count(i) == 0:
                self.negList.append(i)
    
    def addWork(self, rel):
        for i in rel:
            self.peopleDict.ensurePerson(i)
            if self.workList.count(i) == 0:
                self.workList.append(i)
    
    # rel should be a list of tuples (node, relationship type)
    def addRel(self, rel):
        for i in rel:
            if i[1] == "positive":
                self.addPos([i[0]])
            elif i[1] == "negative":
                self.addNeg([i[0]])
            elif i[1] == "working":
                self.addWork([i[0]])
            else:
                raise ValueError(f"Unknown relationship type: {i[1]}")

    # ===Removing relationships===
    def removePos(self, rel):
        for i in rel:
            if i in self.posList:
                self.posList.remove(i)

    def removeNeg(self, rel):
        for i in rel:
            if i in self.negList:
                self.negList.remove(i)
    
    def removeWork(self, rel):
        for i in rel:
            if i in self.workList:
                self.workList.remove(i)

    # ===Getting attributes===
    def getPos(self):
        return self.posList
    
    def getNeg(self):
        return self.negList
    
    def getWork(self):
        return self.workList
    
    def getName(self):
        return self.name
    
    # Getting the relationship between self and someone else, returns empty list if no relationships
    def getRelationship(self, node):
        rel = []
        if self.posList.count(node) != 0:
            rel.append("positive")
        
        if self.negList.count(node) != 0:
            rel.append("negative")
        
        if self.workList.count(node) != 0:
            rel.append("working")
        
        return rel
    
    # ===Changes===
    def changeName(self, newName):
        self.name = newName

    def changePeople(self, people):
        self.people = people
    
    # ===toString===
    def __str__(self):
        lines = [f"Node({self.name})"]

        if self.posList:
            lines.append(f"  + positive: {self.posList}")
        if self.negList:
            lines.append(f"  - negative: {self.negList}")
        if self.workList:
            lines.append(f"  ~ working:  {self.workList}")

        if not (self.posList or self.negList or self.workList):
            lines.append("  (no relationships)")

        return "\n".join(lines)

    

class PeopleDict:
    # ===Constructor===
    def __init__(self, people=None):
        self.people = people or {}
    
    #===Adding people===
    # Ensuring existence of person (if doesn't exist, create this person)
    def ensurePerson(self, name):
        if name not in self.people:
            self.people[name] = Node(name, self)
    
    # Adding multiple people
    def addMultiple(self, names):
        for name in names:
            self.ensurePerson(name)

    # Takes in a list of three-tuples with (a, a's relationship to b, b) and adds the relationships into the correct lists
    # valid relationship types: "positive", "negative", and "working"
    def addRelationships(self, rels):
        for (a, kind, b) in rels:
            self.ensurePerson(a)
            self.ensurePerson(b)

            if kind == "positive":
                self.people[a].addPos([b])
            if kind == "negative":
                self.people[a].addNeg([b])
            if kind == "working":
                self.people[a].addWork([b])
            
            if (kind != "positive") and (kind != "negative") and (kind != "working"):
                raise ValueError(f"Invalid relationship type:  {kind}")
    
    #===Import/Export===
    # Import people from csv list of people
    def addPeopleFromCSV(self, path):
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["from"].strip()
                if name and name not in self.people:
                    self.people[name] = Node(name)
    
    # Import people and relationships from csv list of people and relationships
    def addRelationshipsFromCSV(self, path):
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            
            rels = []

            for row in reader:
                a = row["from"].strip()
                kind = row["type"].strip().lower()
                b = row["to"].strip()
                
                if not a or not kind or not b:
                    continue  # skip blank/bad rows

                rels.append((a, kind, b))

            self.addRelationships(rels)

                
    # Exporting people and relationships to csv list of people and relationships
    def exportRelationshipsToCSV(self, path):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["from", "type", "to"])

            for a, node in self.people.items():
                for b in node.getPos():
                    writer.writerow([a, "positive", b])
                for b in node.getNeg():
                    writer.writerow([a, "negative", b])
                for b in node.getWork():
                    writer.writerow([a, "working", b])

# ==Visualization==
def build_multidigraph(people_dict):
    """
    Converts your PeopleDict into a nx.MultiDiGraph with edge attribute 'rel'.
    Assumes relationship types are: positive, negative, working.
    """
    G = nx.MultiDiGraph()

    # add nodes
    for name in people_dict.people.keys():
        G.add_node(name)

    # add directed multi-edges
    for a, node in people_dict.people.items():
        for b in node.getPos():
            G.add_edge(a, b, rel="positive")
        for b in node.getNeg():
            G.add_edge(a, b, rel="negative")
        for b in node.getWork():
            G.add_edge(a, b, rel="working")

    return G


def _assign_curvatures(G):
    """
    - If a relationship type exists both directions between two nodes:
        draw it "straight-looking" (tiny curvature) and overlap forward/backward.
        Different relationship types get different tiny curvatures, so they don't overlap.
    - If only one direction exists:
        draw it with larger curvature so directionality is readable.
    """
    # Tiny curvature lanes for bidirectional (looks straight, but separable by rel)
    bidir_lane = {
        "positive": 0.02,
        "working":  0.04,
        "negative": 0.06,
    }

    # Larger curvature lanes for one-way edges
    oneway_lane = {
        "positive": 0.18,
        "working":  0.30,
        "negative": 0.42,
    }

    step = 0.08  # if you ever have multiple same-type parallel edges in one direction

    groups = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        rel = d.get("rel", "unknown")
        a, b = sorted((u, v))
        groups.setdefault((a, b, rel), []).append((u, v, k))

    edge_to_rad = {}

    def spread(n, base):
        if n == 1:
            return [base]
        mid = (n - 1) / 2
        return [base + (i - mid) * step for i in range(n)]

    for (a, b, rel), edges in groups.items():
        forward  = [(u, v, k) for (u, v, k) in edges if (u == a and v == b)]
        backward = [(u, v, k) for (u, v, k) in edges if (u == b and v == a)]

        # Bidirectional for this relationship type
        if forward and backward:
            base = bidir_lane.get(rel, 0.03)
            n = max(len(forward), len(backward))
            mags = spread(n, base)

            # Opposite signs => same geometric path, opposite direction arrows
            for i, e in enumerate(forward):
                edge_to_rad[e] = +mags[i]
            for i, e in enumerate(backward):
                edge_to_rad[e] = -mags[i]

        # One-way only
        else:
            base = oneway_lane.get(rel, 0.24)
            mags = spread(len(edges), base)
            for e, m in zip(edges, mags):
                edge_to_rad[e] = +m

    return edge_to_rad



def draw_people_graph(
    people_dict,
    layout="spring",
    seed=7,
    figsize=(11, 8),
    node_size=1600,
    font_size=10,
    show_edge_labels=True,
):
    """
    Draws a curved-arrow relationship graph with multi-edges.
    """

    G = build_multidigraph(people_dict)

    # layout
    if layout == "spring":
        pos = nx.spring_layout(G, seed=seed, k=10 / max(1, math.sqrt(G.number_of_nodes())))
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    else:
        raise ValueError("layout must be one of: spring, kamada_kawai, circular")

    # style maps per relationship type
    rel_style = {
        "positive": dict(color="tab:green", style="solid",  width=2.2),
        "negative": dict(color="tab:red",   style="solid",  width=2.2),
        "working":  dict(color="tab:blue",  style="dashed", width=2.2),
    }

    # draw nodes
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, node_size=node_size)
    nx.draw_networkx_labels(G, pos, font_size=font_size)

    # assign curvature per edge (u,v,k)
    edge_to_rad = _assign_curvatures(G)

    # draw edges by relationship type for consistent legend/styling
    for rel, style in rel_style.items():
        edges_of_type = [(u, v, k) for (u, v, k, d) in G.edges(keys=True, data=True) if d.get("rel") == rel]
        for (u, v, k) in edges_of_type:
            rad = edge_to_rad[(u, v, k)]
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>",
                arrowsize=18,
                width=style["width"],
                edge_color=style["color"],
                style=style["style"],
                min_source_margin=15,
                min_target_margin=15,
            )

    # edge labels (optional)
    if show_edge_labels:
        # Put labels roughly at midpoint; with multi-edges it can get busy,
        # so we label each edge with its relationship type.
        edge_labels = {(u, v, k): G.edges[u, v, k]["rel"] for (u, v, k) in G.edges(keys=True)}
        # networkx label function doesn't natively support keys; fake by drawing per edge
        for (u, v, k), label in edge_labels.items():
            rad = edge_to_rad[(u, v, k)]
            # place label slightly offset along the curve
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            # perpendicular offset proportional to rad
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy) or 1.0
            ox, oy = -dy / length, dx / length
            lx, ly = mx + ox * rad * 0.4, my + oy * rad * 0.4
            plt.text(lx, ly, label, fontsize=9, ha="center", va="center",
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))

    # legend (simple proxies)
    import matplotlib.lines as mlines
    legend_handles = [
        mlines.Line2D([], [], color=rel_style["positive"]["color"], linestyle=rel_style["positive"]["style"], label="positive"),
        mlines.Line2D([], [], color=rel_style["negative"]["color"], linestyle=rel_style["negative"]["style"], label="negative"),
        mlines.Line2D([], [], color=rel_style["working"]["color"],  linestyle=rel_style["working"]["style"],  label="working"),
    ]
    plt.legend(handles=legend_handles, loc="upper left")

    plt.axis("off")
    plt.tight_layout()
    plt.show()

# ===UI===
class RelationshipMatrixUI(tk.Tk):
    def __init__(self, people_dict: PeopleDict, csv_path="relationships.csv", on_change=None):
        super().__init__()
        self.title("Relationship Matrix")
        self.people_dict = people_dict

        self.csv_path = csv_path

        # For noting unsaved changes
        self._dirty = False

        # Snapshot original file so we can discard changes on exit if needed
        self._original_csv_text = ""
        if os.path.exists(self.csv_path):
            with open(self.csv_path, "r", encoding="utf-8") as f:
                self._original_csv_text = f.read()

        self.on_change = on_change # For redrawing graphs.

        self._syncing = False

        # Exiting window works like discarding changes
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Consistent, stable ordering of names alphabetically.
        self.names = sorted(self.people_dict.people.keys())
        self.vars = {}  # (a,b,kind) -> BooleanVar

        # ===Scrollable frame===
        # Containers
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Scrolling
        canvas = tk.Canvas(container)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hscroll = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        self.table = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=self.table, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            # keep the table anchored and allow horizontal expansion
            canvas.itemconfigure(window_id, width=max(event.width, 400))

        self.table.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        self._build_table()

        # Buttons
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=8, pady=8)

        ttk.Button(btn_row, text="Save", command=self._save).pack(side="left")
        ttk.Button(btn_row, text="Save & Exit", command=self._save_and_exit).pack(side="left", padx=8)
        ttk.Button(btn_row, text="Exit (Don’t Save)", command=self._exit_no_save).pack(side="right")

        # Save/unsaved status
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=8, pady=(0, 8))

    # ===Saving and/or Exit Methods===
    def _save(self):
        # Overwrite relationships.csv
        self.people_dict.exportRelationshipsToCSV(self.csv_path)
        self._dirty = False
        print(f"Saved to {self.csv_path}")

    def _save_and_exit(self):
        self._save()
        self.destroy()

    def _exit_no_save(self):
        # Restore original CSV content into the PeopleDict, then close.
        self.people_dict.people.clear()

        if self._original_csv_text.strip():
            # Write snapshot to a temp file-like path and reload
            # (PeopleDict reads from a path, so simplest is to re-read via a real temp file)
            tmp_path = self.csv_path + ".__tmp_restore__"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(self._original_csv_text)

            self.people_dict.addRelationshipsFromCSV(tmp_path)

            try:
                os.remove(tmp_path)
            except OSError:
                pass

        self._dirty = False
        self.status_var.set("Exited without saving: discarded changes")
        self.destroy()


    def _build_table(self):
        names = self.names

        # Header row: blank corner + column names (names of people)
        ttk.Label(self.table, text="from \\ to", padding=4).grid(row=0, column=0, sticky="nsew")
        for j, b in enumerate(names, start=1):
            ttk.Label(self.table, text=b, padding=4).grid(row=0, column=j, sticky="nsew")

        # Each row: row label (names of people) + cells
        for i, a in enumerate(names, start=1):
            ttk.Label(self.table, text=a, padding=4).grid(row=i, column=0, sticky="nsew")

            for j, b in enumerate(names, start=1):
                cell = ttk.Frame(self.table, padding=2)
                cell.grid(row=i, column=j, sticky="nsew")

                # Disables self-relationships
                if a == b:
                    ttk.Label(cell, text="—").pack()
                    continue
                
                # Reading exisiting data
                node_a = self.people_dict.people[a]

                # Initial values
                init_pos = node_a.hasPos(b) if hasattr(node_a, "hasPos") else (b in node_a.getPos())
                init_neg = node_a.hasNeg(b) if hasattr(node_a, "hasNeg") else (b in node_a.getNeg())
                init_work = node_a.hasWork(b) if hasattr(node_a, "hasWork") else (b in node_a.getWork())

                vpos = tk.BooleanVar(value=init_pos)
                vneg = tk.BooleanVar(value=init_neg)
                vwrk = tk.BooleanVar(value=init_work)

                self.vars[(a, b, "positive")] = vpos
                self.vars[(a, b, "negative")] = vneg
                self.vars[(a, b, "working")]  = vwrk

                # Three small checkbuttons stacked (or pack side-by-side if you prefer)
                ttk.Checkbutton(
                    cell, text="+", variable=vpos,
                    command=lambda A=a, B=b: self._toggle(A, B, "positive")
                ).pack(anchor="w")

                ttk.Checkbutton(
                    cell, text="-", variable=vneg,
                    command=lambda A=a, B=b: self._toggle(A, B, "negative")
                ).pack(anchor="w")

                ttk.Checkbutton(
                    cell, text="~", variable=vwrk,
                    command=lambda A=a, B=b: self._toggle(A, B, "working")
                ).pack(anchor="w")

        # make grid cells stretch nicer
        for c in range(len(names) + 1):
            self.table.columnconfigure(c, weight=1)

    # Called whenever a checkbox changes
    def _toggle(self, a, b, kind):
        self.people_dict.ensurePerson(a)
        self.people_dict.ensurePerson(b)
        node_a = self.people_dict.people[a]

        v = self.vars[(a, b, kind)].get()

        if kind == "positive":
            if v: node_a.addPos([b])
            else:
                if hasattr(node_a, "safeRemovePos"): node_a.safeRemovePos(b)
                else:
                    if b in node_a.getPos(): node_a.removePos([b])

        elif kind == "negative":
            if v: node_a.addNeg([b])
            else:
                if hasattr(node_a, "safeRemoveNeg"): node_a.safeRemoveNeg(b)
                else:
                    if b in node_a.getNeg(): node_a.removeNeg([b])

        elif kind == "working":
            if v: node_a.addWork([b])
            else:
                if hasattr(node_a, "safeRemoveWork"): node_a.safeRemoveWork(b)
                else:
                    if b in node_a.getWork(): node_a.removeWork([b])

        # optional callback (e.g., redraw graph)
        if self.on_change:
            self.on_change()
        
        # Notes unsaved changes
        self._dirty = True
        self.status_var.set("Unsaved changes")

   
    # Apply one directional change (a -> b) to PeopleDict using Node methods.
    def _apply_model_change(self, a, b, kind, checked: bool):
        self.people_dict.ensurePerson(a)
        self.people_dict.ensurePerson(b)
        node_a = self.people_dict.people[a]

        if kind == "positive":
            if checked:
                node_a.addPos([b])
            else:
                if hasattr(node_a, "safeRemovePos"):
                    node_a.safeRemovePos(b)
                else:
                    if b in node_a.getPos():
                        node_a.removePos([b])

        elif kind == "negative":
            if checked:
                node_a.addNeg([b])
            else:
                if hasattr(node_a, "safeRemoveNeg"):
                    node_a.safeRemoveNeg(b)
                else:
                    if b in node_a.getNeg():
                        node_a.removeNeg([b])

        elif kind == "working":
            if checked:
                node_a.addWork([b])
            else:
                if hasattr(node_a, "safeRemoveWork"):
                    node_a.safeRemoveWork(b)
                else:
                    if b in node_a.getWork():
                        node_a.removeWork([b])

        else:
            raise ValueError(f"Unknown kind: {kind}")

    # Set UI checkbox state if it exists (won't call _toggle).
    def _set_checkbox(self, a, b, kind, checked: bool):
        key = (a, b, kind)
        var = self.vars.get(key)
        if var is not None:
            var.set(checked)
    
    def _on_window_close(self):
        if not self._dirty:
            self.destroy()
            return

        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            "You have unsaved changes.\n\nYes = Save & Exit\nNo = Exit (Don’t Save)\nCancel = Keep editing"
        )

        if choice is True:
            self._save_and_exit()
        elif choice is False:
            self._exit_no_save()
        else:
            # Cancel and do nothing
            return



# ===Testing===

# ===Main===
'''
relationships = PeopleDict()
relationships.addRelationshipsFromCSV("relationships.csv")
draw_people_graph(relationships, layout="spring", show_edge_labels=False)
'''

if __name__ == "__main__":
    relationships = PeopleDict()
    relationships.addRelationshipsFromCSV("relationships.csv")

    # Launch the table UI
    app = RelationshipMatrixUI(relationships, csv_path="relationships.csv")
    # Starts the UI and blocks until you close it
    app.mainloop()

    # After you close the UI, draw the graph (using edited relationships)
    draw_people_graph(relationships, layout="spring", show_edge_labels=False)

