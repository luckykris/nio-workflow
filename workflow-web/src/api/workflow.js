import request from '@/utils/request'

export function getWorkflowTemplate(params) {
  return request({
    url: '/v1/workflow_template/',
    method: 'get',
    params
  })
}

export function getWorkflowTemplateDetail(id) {
  return request({
    url: '/v1/workflow_template/' + id.toString(),
    method: 'get'
  })
}

export function addWorkflowTemplate(data) {
  return request({
    url: '/v1/workflow_template/',
    method: 'post',
    data: data
  })
}

export function addStepDefine(wt_id, name) {
  return request({
    url: '/v1/step_define/',
    method: 'post',
    data: { workflow_template: wt_id, name: name}
  })
}

export function deleteStepDefine(id) {
  return request({
    url: '/v1/step_define/' + id.toString() + '/',
    method: 'delete',
  })
}

export function linkStepDefine(from_id, to_id, type) {
  return request({
    url: '/v1/step_define/' + from_id.toString() + '/link/',
    method: 'post',
    data: { to: to_id, type: type}
  })
}

export function deletelinkStepDefine(from_id, to_id, type) {
  return request({
    url: '/v1/step_define/' + from_id.toString() + '/link/',
    method: 'delete',
    data: { to: to_id, type: type}
  })
}

export function updateStepDefine(data) {
  return request({
    url: '/v1/step_define/' + data.id.toString() + '/' ,
    method: 'put',
    data: data
  })
}
