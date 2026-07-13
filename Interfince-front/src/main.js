import App from './App'

import store from './vuex/store'

import routes from './routes'

Vue.config.productionTip = false;

Vue.use(ELEMENT);
Vue.use(VueRouter);
Vue.use(Vuex);


const router = new VueRouter({
  routes
});

router.beforeEach((to, from, next) => {
  //NProgress.start();
  if (to.path === '/login') {
    localStorage.removeItem('token');
  }
  let token = localStorage.getItem('token');
  if (token === 'undefined'){
      token = ''
  }

  if (!token && to.path === '/register') {
      next()
  }
  else if (!token && to.path !== '/login') {
    console.log(to.path);
    next({ path: '/login', query: {url: to.path}})
  }
  else {
    next()
  }
  if (to.path === '/') {
    next({ path: '/projectList',})
  }
});


let Highlight = {};
Highlight.install = function (Vue, options) {
    // 先有数据再绑定，调用highlightA
    Vue.directive('highlightA', {
        inserted: function(el, binding) {
            el.innerText = binding.value
            hljs.highlightBlock(el)
        },
        update: function(el, binding) {
            el.innerText = binding.value
            // console.log("binding value:",el)
            hljs.highlightBlock(el)
        }
    });
    // 先绑定，后面会有数据更新，调用highlightB
    Vue.directive('highlightB', {
        componentUpdated: function(el) {
            let blocks = el.querySelectorAll('pre code');
            for (let i = 0; i < blocks.length; i++) {
                const item = blocks[i];
                hljs.highlightBlock(item);
            };
        }
    });
};

Vue.use(Highlight);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');

