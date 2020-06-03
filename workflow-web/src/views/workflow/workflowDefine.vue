<template>
  <div class="app-container">
    <el-button
      @click="addNewStepDefine"
    >
      +
    </el-button>
    <!--<el-button-->
      <!--@click="decodeGojsFormate"-->
    <!--&gt;-->
      <!--Save-->
    <!--</el-button>-->
    <diagram
      ref="diag"
      :selectionDeleting="selectionDeleting"
      :linkDrawn="linkDrawn"
      :textEdited="textEdited"
      v-bind:model-data="diagramData"
      v-on:model-changed="modelChanged"
      v-on:changed-selection="changedSelection"
      style="border: solid 1px black; width:100%; height:400px">
    </diagram>
  </div>
</template>
<script>
  import diagram from './components/diagram'
  import {
    getWorkflowTemplateDetail,
    addStepDefine,
    linkStepDefine,
    updateStepDefine,
    deletelinkStepDefine,
    deleteStepDefine,
  } from '@/api/workflow'
  export default {
    name: "workflowDefine",
    components:{ diagram},
    data(){
      return {
        id: this.$route.params.id,
        originData: {},
        diagramData: {  // passed to <diagram> as its modelData
          class: "go.GraphLinksModel",
          copiesArrays: true,
          "copiesArrayObjects": true,
          nodeCategoryProperty: "type",
          linkFromPortIdProperty: "frompid",
          linkToPortIdProperty: "topid",
          nodeDataArray: [
            // {"key":1, "type":"StepDefine", "name":"Product"},
            // {"key":2, "type":"StepDefine", "name":"Product"},
            // {"key":3, "type":"StepDefine", "name":"Product"},
          ],
          linkDataArray: [
            // {"from":1, "frompid":"COMMIT", "to":2, "topid":"INPUT"},
            // { from: 1, to: 2 },
            // { from: 1, to: 3 },
            // { from: 3, to: 4 },
            // { from: 2, to: 4 },
            // { from: 4, to: 5 },
            // { from: 7, to: 5 },
            // { from: 8, to: 5 },

          ]
        }
      }
    },
    watch:{
        "$route.params.id":{
            handler(curVal,oldVal){
                // console.log(curVal)
                if(curVal == oldVal){
                  return
                }
                this.id = curVal
                this.reload()
            }
        }
    },
    created(){
      this.reload()
    },
    methods:{
      selectionDeleting(e) {
        e.subject.toList().j.forEach(
          (v,k)=> {
            let delete_d = v.part.data
            if(delete_d.from!=undefined){
              deletelinkStepDefine(delete_d.from, delete_d.to, delete_d.frompid)
                .then(
                  console.log('success')
                )
            }else if(delete_d.key!=undefined){
              deleteStepDefine(delete_d.key)
                .then(
                  console.log('success')
                )
            }
          }
        )
      },
      textEdited(e){
        let k = e.subject.part.data.key
        let name = e.subject.text
        let old_name = e.subject.parameter
        this.originData[k].name = name
        updateStepDefine(this.originData[k])
          .then(
            response=>{
              this.originData[k]=response
            }
          ).catch(
            e=>{
              this.originData[k].old_name
            }
          )
      },
      linkDrawn(e) {
        let to = e.subject.data.to
        let from = e.subject.data.from
        let frompid = e.subject.data.frompid
        linkStepDefine(from,to,frompid)
          .then(
            response =>{
              console.log('success')
            }
          ).catch(
          e =>{
            this.reload()
          }
        )
      },
      reload(){
        if(this.id == null){
          return
        }
        this.originData={}
        getWorkflowTemplateDetail(this.id)
          .then(
            response =>{
              this.encodeGojsFormate(response.step_defines)
            }
          )
      },
      encodeGojsFormate(steps_data){
        let r = []
        let rl = []
        steps_data.forEach(
          (v,k) =>{
            this.originData[v.id] = v
            // console.log(v)
            r.push({'type': 'StepDefine', 'name': v.name, 'key': v.id})
            v.commit_stepdefines.forEach(
              (v2,k2)=>{
                rl.push({"from":v.id, "frompid":"COMMIT", "to":v2, "topid":"INPUT"})
              }
            )
            v.fail_stepdefines.forEach(
              (v2,k2)=>{
                rl.push({"from":v.id, "frompid":"FAIL", "to":v2, "topid":"INPUT"})
              }
            )
            v.reject_stepdefines.forEach(
              (v2,k2)=>{
                rl.push({"from":v.id, "frompid":"REJECT", "to":v2, "topid":"INPUT"})
              }
            )
            v.success_stepdefines.forEach(
              (v2,k2)=>{
                rl.push({"from":v.id, "frompid":"SUCCESS", "to":v2, "topid":"INPUT"})
              }
            )
          }
        )
        this.diagramData.nodeDataArray = r
        this.diagramData.linkDataArray = rl
        return null
      },
      decodeGojsFormate(){
        let steps_deine_map = {}
        this.diagramData.nodeDataArray.forEach(
          (v,k)=>{
            steps_deine_map[v.key] = {
              id: v.key,
              name: v.name,
              commit_stepdefines: [],
              fail_stepdefines: [],
              success_stepdefines: [],
              reject_stepdefines: [],
            }
          }
        )
        this.diagramData.linkDataArray.forEach(
          (v,k)=>{
            if(v.frompid == 'COMMIT') {
              steps_deine_map[v.from].commit_stepdefines.push(v.to)
            }else if(v.frompid == 'FAIL'){
              steps_deine_map[v.from].fail_stepdefines.push(v.to)
            }else if(v.frompid == 'SUCCESS'){
              steps_deine_map[v.from].success_stepdefines.push(v.to)
            }else if(v.frompid == 'REJECT'){
              steps_deine_map[v.from].reject_stepdefines.push(v.to)
            }
          }
        )
        // console.log(Object.values(steps_deine_map))
        return Object.values(steps_deine_map)
      },
      addNewStepDefine(){
        addStepDefine(this.id, "New Step Define")
          .then(
            response =>{
              this.reload()
            }
          )
      },
      modelChanged: function(e) {
        if (e.isTransactionFinished) {  // show the model data in the page's TextArea
          this.savedModelText = e.model.toJson();
        }
      },
      changedSelection: function(e) {
        var node = e.diagram.selection.first();
        if (node instanceof go.Node) {
          this.currentNode = node;
          this.currentNodeText = node.data.text;
        } else {
          this.currentNode = null;
          this.currentNodeText = "";
        }
      },
    }
  }
</script>
