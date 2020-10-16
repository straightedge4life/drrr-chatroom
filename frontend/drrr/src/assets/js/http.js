import axios from 'axios'

let instance = axios.create({
    headers: {'content-type': 'application/json'},
})


// 添加响应拦截器
instance.interceptors.response.use(function (response) {
    // 对响应数据做点什么  
    if (response.status == "200") {
        
    }
    return response.data
}, function (error) {
    // 对响应错误做点什么
    console.log('--- 401 res error response ---')
    
    return Promise.reject(error)
})

export default instance


