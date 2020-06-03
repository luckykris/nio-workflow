<template>
</template>
<script>
import go from 'gojs'
let $ = go.GraphObject.make
export default{
	name : 'diagram',
	props: ['modelData', 'linkDrawn', 'textEdited', 'selectionDeleting'],
	data(){
		return {diagram: null, palette: null}
	},
	mounted: function() {
          var self = this;
          var myDiagram =
            $(go.Diagram, this.$el,
              {
                initialContentAlignment: go.Spot.Left,
                initialAutoScale: go.Diagram.UniformToFill,
                layout: $(go.LayeredDigraphLayout, { direction: 0 }),
                "undoManager.isEnabled": true,
              });
          // myDiagram.nodeTemplate =
          //   $(go.Node, "Auto",
          //     $(go.Shape,
          //       {
          //         fill: "white", strokeWidth: 0,
          //         portId: "", fromLinkable: true, toLinkable: false, cursor: "pointer"
          //       },
          //       new go.Binding("fill", "color")),
          //     $(go.TextBlock,
          //       { margin: 8, editable: false },
          //       new go.Binding("text").makeTwoWay())
          //   );
          // when the document is modified, add a "*" to the title and enable the "Save" button
          myDiagram.addDiagramListener("Modified", function(e) {
            var button = document.getElementById("SaveButton");
            if (button) button.disabled = !myDiagram.isModified;
            var idx = document.title.indexOf("*");
            if (myDiagram.isModified) {
              if (idx < 0) document.title += "*";
            } else {
              if (idx >= 0) document.title = document.title.substr(0, idx);
            }
          });
          // SelectionDeleting
          myDiagram.addDiagramListener("SelectionDeleting", this.selectionDeleting)
          // TextEdited
          myDiagram.addDiagramListener("TextEdited", this.textEdited)
          // linkdrawn
          myDiagram.addDiagramListener("LinkDrawn", this.linkDrawn)
          // To simplify this code we define a function for creating a context menu button:
          function makeButton(text, action, visiblePredicate) {
            return $("ContextMenuButton",
              $(go.TextBlock, text),
              { click: action },
              // don't bother with binding GraphObject.visible if there's no predicate
              visiblePredicate ? new go.Binding("visible", "", function(o, e) { return o.diagram ? visiblePredicate(o, e) : false; }).ofObject() : {});
          }

          var nodeMenu = $("ContextMenu",
            makeButton("Add Fail Loop",
              function(e, obj) {
                e.diagram.model.linkDataArray.push({"from":obj.part.key, "frompid":"FAIL", "to":obj.part.key, "topid":"INPUT"});
              }
            )
          );

          function makePort(name, leftside) {
            var port = $(go.Shape, "Rectangle",
              {
                fill: "gray", stroke: null,
                desiredSize: new go.Size(8, 8),
                portId: name,  // declare this object to be a "port"
                toMaxLinks: 10,  // don't allow more than one link into a port
                cursor: "pointer"  // show a different cursor to indicate potential link point
              });

            var lab = $(go.TextBlock, name,  // the name of the port
              { font: "7pt sans-serif" });

            var panel = $(go.Panel, "Horizontal",
              { margin: new go.Margin(2, 0) });

            // set up the port/panel based on which side of the node it will be on
            if (leftside) {
              port.toSpot = go.Spot.Left;
              port.toLinkable = true;
              lab.margin = new go.Margin(1, 0, 0, 1);
              panel.alignment = go.Spot.TopLeft;
              panel.add(port);
              panel.add(lab);
            } else {
              port.fromSpot = go.Spot.Right;
              port.fromLinkable = true;
              lab.margin = new go.Margin(1, 1, 0, 0);
              panel.alignment = go.Spot.TopRight;
              panel.add(lab);
              panel.add(port);
            }
            return panel;
          }

          function makeTemplate(typename, icon, background, inports, outports) {
            var node = $(go.Node, "Spot",
              {
                contextMenu: nodeMenu,
              },
              $(go.Panel, "Auto",
                {
                  width: 100,
                  height: 120
                },
                $(go.Shape, "Rectangle",
                  {
                    fill: '',
                    stroke: null, strokeWidth: 0,
                    spot1: go.Spot.TopLeft, spot2: go.Spot.BottomRight
                  }),
                $(go.Panel, "Table",
                  $(go.TextBlock, typename,
                    {
                      row: 0,
                      margin: 3,
                      maxSize: new go.Size(80, NaN),
                      stroke: "white",
                      font: "bold 11pt sans-serif"
                    }),
                  $(go.Picture, icon,
                    { row: 1, width: 55, height: 55 }),
                  $(go.TextBlock,
                    {
                      row: 2,
                      margin: 3,
                      editable: true,
                      maxSize: new go.Size(80, 40),
                      stroke: "white",
                      font: "bold 9pt sans-serif"
                    },
                    new go.Binding("text", "name").makeTwoWay())
                )
              ),
              $(go.Panel, "Vertical",
                {
                  alignment: go.Spot.Left,
                  toLinkableSelfNode:true,
                  fromLinkableSelfNode:true,
                  alignmentFocus: new go.Spot(0, 0.5, 8, 0)
                },
                inports),
              $(go.Panel, "Vertical",
                {
                  alignment: go.Spot.Right,
                  alignmentFocus: new go.Spot(1, 0.5, -8, 0)
                },
                outports)
            );
            myDiagram.nodeTemplateMap.set(typename, node);
          }
          makeTemplate("StepDefine", "color", "forestgreen",
            [makePort("INPUT", true)],
            [makePort("COMMIT", false), makePort("REJECT", false), makePort("SUCCESS", false), makePort("FAIL", false)]
          );
          myDiagram.linkTemplate =
            $(go.Link,
              {
                routing: go.Link.Orthogonal,
                corner: 5,
                curve: go.Link.JumpGap,
                reshapable: true,
                resegmentable: true,
                relinkableFrom: true,
                relinkableTo: true
              },
              $(go.Shape, { stroke: "gray", strokeWidth: 2 }),
              $(go.Shape, { stroke: "gray", fill: "gray", toArrow: "Standard" })
            );

          this.diagram = myDiagram;
          this.palette = new go.Palette(this.$refs['palette']);  // create a new Palette in the HTML DIV element "palette"
          this.palette.nodeTemplateMap = this.diagram.nodeTemplateMap;
          this.palette.model.nodeDataArray = [{category:'StepDefine'}]
          this.updateModel(this.modelData);
        },
	watch: {
	  modelData: {
	  	handler(val,val_old) { this.updateModel(val)},
	  	deep:true
	  }
	},
	methods: {
	  model: function() { return this.diagram.model; },
	  updateModel: function(val) {
	    // No GoJS transaction permitted when replacing Diagram.model.
	    if (val instanceof go.Model) {
	      this.diagram.model = val;
	    } else {
	      var m = new go.GraphLinksModel()
	      if (val) {
	        for (var p in val) {
	          m[p] = val[p];
	        }
	      }
	      this.diagram.model = m;
	    }
	  },
	  updateDiagramFromData: function() {
	    this.diagram.startTransaction();
	    // This is very general but very inefficient.
	    // It would be better to modify the diagramData data by calling
	    // Model.setDataProperty or Model.addNodeData, et al.
	    this.diagram.updateAllRelationshipsFromData();
	    this.diagram.updateAllTargetBindings();
	    this.diagram.commitTransaction("updated");
	  }
	}
 }

</script>
