webpackJsonp([12],{530:function(t,e,r){"use strict";function n(t){return t&&t.__esModule?t:{default:t}}Object.defineProperty(e,"__esModule",{value:!0});var o=r(136),a=n(o),i=r(51),s=n(i),u=r(3),f=n(u),c=r(792),d=function(t){if(t&&t.__esModule)return t;var e={};if(null!=t)for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&(e[r]=t[r]);return e.default=t,e}(c),l=r(579),h=n(l);e.default={namespace:"Cloudconfigmodel",state:{cloudData:[],Clouddatals:[],thirdpartdatals:[],page:null},reducers:{save:function(t,e){var r=e.payload,n=r.data,o=r.dataCloudlist,a=r.ThirdpartynameData,i=r.page,u=a.data,c=o.data,d=[],l=[],h=!0,p=!1,y=void 0;try{for(var b,v=(0,s.default)(u);!(h=(b=v.next()).done);h=!0){var m=b.value;d.push(m.thirdpartname)}}catch(t){p=!0,y=t}finally{try{!h&&v.return&&v.return()}finally{if(p)throw y}}var w=!0,_=!1,x=void 0;try{for(var g,A=(0,s.default)(c);!(w=(g=A.next()).done);w=!0){var T=g.value;l.push(T.cloudid)}}catch(t){_=!0,x=t}finally{try{!w&&A.return&&A.return()}finally{if(_)throw x}}return(0,f.default)({},t,{cloudData:n,Clouddatals:l,thirdpartdatals:d,page:i})}},effects:{fetchCloudconfig:a.default.mark(function t(e,r){var n,o,i,s,u,f=e.payload.page,c=void 0===f?1:f,l=r.call,h=r.put;return a.default.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,l(d.fetchyun,c);case 2:return n=t.sent,o=n.data,i=1,t.next=7,l(d.fetchsTh,i);case 7:return s=t.sent,t.next=10,l(d.fetchname);case 10:return u=t.sent,t.next=13,h({type:"save",payload:{data:o,dataCloudlist:u,ThirdpartynameData:s,page:parseInt(c,10)}});case 13:case"end":return t.stop()}},t,this)}),saveCloudconfig:a.default.mark(function t(e,r){var n,o,i,s,u,f,c,l=e.payload,h=r.call,p=r.put;return a.default.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n=l.typeThird,o=l.value,i=l.resolve,s=l.reject,u=o.cloudid,f=o.thirdpart,t.next=4,h(d.savename,u,f,n);case 4:return c=t.sent,c?(console.log(c.data),i(c.data)):s(c),t.next=8,p({type:"reload"});case 8:case"end":return t.stop()}},t,this)}),reload:a.default.mark(function t(e,r){var n,o=r.put,i=r.select;return a.default.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,i(function(t){return t.Cloudconfigmodel.page});case 2:return n=t.sent,t.next=5,o({type:"fetchCloudconfig",payload:{page:n}});case 5:case"end":return t.stop()}},t,this)})},subscriptions:{setup:function(t){var e=t.dispatch;return t.history.listen(function(t){var r=t.pathname,n=t.search,o=h.default.parse(n);"/Cloudconfig"===r&&e({type:"fetchCloudconfig",payload:o})})}}},t.exports=e.default},549:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:!0});e.PAGE_SIZE=8},570:function(t,e,r){"use strict";function n(t){return t&&t.__esModule?t:{default:t}}function o(t){if(t.status>=200&&t.status<300)return t;var e=new Error(t.statusText);throw e.response=t,e}Object.defineProperty(e,"__esModule",{value:!0});var a=r(136),i=n(a),s=r(575),u=n(s),f=r(576),c=n(f);e.default=function(){function t(t,r){return e.apply(this,arguments)}var e=(0,u.default)(i.default.mark(function t(e,r){var n,a,s;return i.default.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,(0,c.default)(e,r);case 2:return n=t.sent,o(n),t.next=6,n.json();case 6:return a=t.sent,s={data:a,headers:{}},n.headers.get("x-total-count")&&(s.headers["x-total-count"]=n.headers.get("x-total-count")),t.abrupt("return",s);case 10:case"end":return t.stop()}},t,this)}));return t}(),t.exports=e.default},575:function(t,e,r){"use strict";e.__esModule=!0;var n=r(138),o=function(t){return t&&t.__esModule?t:{default:t}}(n);e.default=function(t){return function(){var e=t.apply(this,arguments);return new o.default(function(t,r){function n(a,i){try{var s=e[a](i),u=s.value}catch(t){return void r(t)}if(!s.done)return o.default.resolve(u).then(function(t){n("next",t)},function(t){n("throw",t)});t(u)}return n("next")})}}},576:function(t,e,r){t.exports=r(577)},577:function(t,e,r){r(578),t.exports=self.fetch.bind(self)},578:function(t,e){!function(t){"use strict";function e(t){if("string"!=typeof t&&(t=String(t)),/[^a-z0-9\-#$%&'*+.\^_`|~]/i.test(t))throw new TypeError("Invalid character in header field name");return t.toLowerCase()}function r(t){return"string"!=typeof t&&(t=String(t)),t}function n(t){var e={next:function(){var e=t.shift();return{done:void 0===e,value:e}}};return v.iterable&&(e[Symbol.iterator]=function(){return e}),e}function o(t){this.map={},t instanceof o?t.forEach(function(t,e){this.append(e,t)},this):Array.isArray(t)?t.forEach(function(t){this.append(t[0],t[1])},this):t&&Object.getOwnPropertyNames(t).forEach(function(e){this.append(e,t[e])},this)}function a(t){if(t.bodyUsed)return Promise.reject(new TypeError("Already read"));t.bodyUsed=!0}function i(t){return new Promise(function(e,r){t.onload=function(){e(t.result)},t.onerror=function(){r(t.error)}})}function s(t){var e=new FileReader,r=i(e);return e.readAsArrayBuffer(t),r}function u(t){var e=new FileReader,r=i(e);return e.readAsText(t),r}function f(t){for(var e=new Uint8Array(t),r=new Array(e.length),n=0;n<e.length;n++)r[n]=String.fromCharCode(e[n]);return r.join("")}function c(t){if(t.slice)return t.slice(0);var e=new Uint8Array(t.byteLength);return e.set(new Uint8Array(t)),e.buffer}function d(){return this.bodyUsed=!1,this._initBody=function(t){if(this._bodyInit=t,t)if("string"==typeof t)this._bodyText=t;else if(v.blob&&Blob.prototype.isPrototypeOf(t))this._bodyBlob=t;else if(v.formData&&FormData.prototype.isPrototypeOf(t))this._bodyFormData=t;else if(v.searchParams&&URLSearchParams.prototype.isPrototypeOf(t))this._bodyText=t.toString();else if(v.arrayBuffer&&v.blob&&w(t))this._bodyArrayBuffer=c(t.buffer),this._bodyInit=new Blob([this._bodyArrayBuffer]);else{if(!v.arrayBuffer||!ArrayBuffer.prototype.isPrototypeOf(t)&&!_(t))throw new Error("unsupported BodyInit type");this._bodyArrayBuffer=c(t)}else this._bodyText="";this.headers.get("content-type")||("string"==typeof t?this.headers.set("content-type","text/plain;charset=UTF-8"):this._bodyBlob&&this._bodyBlob.type?this.headers.set("content-type",this._bodyBlob.type):v.searchParams&&URLSearchParams.prototype.isPrototypeOf(t)&&this.headers.set("content-type","application/x-www-form-urlencoded;charset=UTF-8"))},v.blob&&(this.blob=function(){var t=a(this);if(t)return t;if(this._bodyBlob)return Promise.resolve(this._bodyBlob);if(this._bodyArrayBuffer)return Promise.resolve(new Blob([this._bodyArrayBuffer]));if(this._bodyFormData)throw new Error("could not read FormData body as blob");return Promise.resolve(new Blob([this._bodyText]))},this.arrayBuffer=function(){return this._bodyArrayBuffer?a(this)||Promise.resolve(this._bodyArrayBuffer):this.blob().then(s)}),this.text=function(){var t=a(this);if(t)return t;if(this._bodyBlob)return u(this._bodyBlob);if(this._bodyArrayBuffer)return Promise.resolve(f(this._bodyArrayBuffer));if(this._bodyFormData)throw new Error("could not read FormData body as text");return Promise.resolve(this._bodyText)},v.formData&&(this.formData=function(){return this.text().then(p)}),this.json=function(){return this.text().then(JSON.parse)},this}function l(t){var e=t.toUpperCase();return x.indexOf(e)>-1?e:t}function h(t,e){e=e||{};var r=e.body;if(t instanceof h){if(t.bodyUsed)throw new TypeError("Already read");this.url=t.url,this.credentials=t.credentials,e.headers||(this.headers=new o(t.headers)),this.method=t.method,this.mode=t.mode,r||null==t._bodyInit||(r=t._bodyInit,t.bodyUsed=!0)}else this.url=String(t);if(this.credentials=e.credentials||this.credentials||"omit",!e.headers&&this.headers||(this.headers=new o(e.headers)),this.method=l(e.method||this.method||"GET"),this.mode=e.mode||this.mode||null,this.referrer=null,("GET"===this.method||"HEAD"===this.method)&&r)throw new TypeError("Body not allowed for GET or HEAD requests");this._initBody(r)}function p(t){var e=new FormData;return t.trim().split("&").forEach(function(t){if(t){var r=t.split("="),n=r.shift().replace(/\+/g," "),o=r.join("=").replace(/\+/g," ");e.append(decodeURIComponent(n),decodeURIComponent(o))}}),e}function y(t){var e=new o;return t.split(/\r?\n/).forEach(function(t){var r=t.split(":"),n=r.shift().trim();if(n){var o=r.join(":").trim();e.append(n,o)}}),e}function b(t,e){e||(e={}),this.type="default",this.status="status"in e?e.status:200,this.ok=this.status>=200&&this.status<300,this.statusText="statusText"in e?e.statusText:"OK",this.headers=new o(e.headers),this.url=e.url||"",this._initBody(t)}if(!t.fetch){var v={searchParams:"URLSearchParams"in t,iterable:"Symbol"in t&&"iterator"in Symbol,blob:"FileReader"in t&&"Blob"in t&&function(){try{return new Blob,!0}catch(t){return!1}}(),formData:"FormData"in t,arrayBuffer:"ArrayBuffer"in t};if(v.arrayBuffer)var m=["[object Int8Array]","[object Uint8Array]","[object Uint8ClampedArray]","[object Int16Array]","[object Uint16Array]","[object Int32Array]","[object Uint32Array]","[object Float32Array]","[object Float64Array]"],w=function(t){return t&&DataView.prototype.isPrototypeOf(t)},_=ArrayBuffer.isView||function(t){return t&&m.indexOf(Object.prototype.toString.call(t))>-1};o.prototype.append=function(t,n){t=e(t),n=r(n);var o=this.map[t];this.map[t]=o?o+","+n:n},o.prototype.delete=function(t){delete this.map[e(t)]},o.prototype.get=function(t){return t=e(t),this.has(t)?this.map[t]:null},o.prototype.has=function(t){return this.map.hasOwnProperty(e(t))},o.prototype.set=function(t,n){this.map[e(t)]=r(n)},o.prototype.forEach=function(t,e){for(var r in this.map)this.map.hasOwnProperty(r)&&t.call(e,this.map[r],r,this)},o.prototype.keys=function(){var t=[];return this.forEach(function(e,r){t.push(r)}),n(t)},o.prototype.values=function(){var t=[];return this.forEach(function(e){t.push(e)}),n(t)},o.prototype.entries=function(){var t=[];return this.forEach(function(e,r){t.push([r,e])}),n(t)},v.iterable&&(o.prototype[Symbol.iterator]=o.prototype.entries);var x=["DELETE","GET","HEAD","OPTIONS","POST","PUT"];h.prototype.clone=function(){return new h(this,{body:this._bodyInit})},d.call(h.prototype),d.call(b.prototype),b.prototype.clone=function(){return new b(this._bodyInit,{status:this.status,statusText:this.statusText,headers:new o(this.headers),url:this.url})},b.error=function(){var t=new b(null,{status:0,statusText:""});return t.type="error",t};var g=[301,302,303,307,308];b.redirect=function(t,e){if(-1===g.indexOf(e))throw new RangeError("Invalid status code");return new b(null,{status:e,headers:{location:t}})},t.Headers=o,t.Request=h,t.Response=b,t.fetch=function(t,e){return new Promise(function(r,n){var o=new h(t,e),a=new XMLHttpRequest;a.onload=function(){var t={status:a.status,statusText:a.statusText,headers:y(a.getAllResponseHeaders()||"")};t.url="responseURL"in a?a.responseURL:t.headers.get("X-Request-URL");var e="response"in a?a.response:a.responseText;r(new b(e,t))},a.onerror=function(){n(new TypeError("Network request failed"))},a.ontimeout=function(){n(new TypeError("Network request failed"))},a.open(o.method,o.url,!0),"include"===o.credentials&&(a.withCredentials=!0),"responseType"in a&&v.blob&&(a.responseType="blob"),o.headers.forEach(function(t,e){a.setRequestHeader(e,t)}),a.send(void 0===o._bodyInit?null:o._bodyInit)})},t.fetch.polyfill=!0}}("undefined"!=typeof self?self:this)},579:function(t,e,r){"use strict";function n(t){switch(t.arrayFormat){case"index":return function(e,r,n){return null===r?[a(e,t),"[",n,"]"].join(""):[a(e,t),"[",a(n,t),"]=",a(r,t)].join("")};case"bracket":return function(e,r){return null===r?a(e,t):[a(e,t),"[]=",a(r,t)].join("")};default:return function(e,r){return null===r?a(e,t):[a(e,t),"=",a(r,t)].join("")}}}function o(t){var e;switch(t.arrayFormat){case"index":return function(t,r,n){if(e=/\[(\d*)\]$/.exec(t),t=t.replace(/\[\d*\]$/,""),!e)return void(n[t]=r);void 0===n[t]&&(n[t]={}),n[t][e[1]]=r};case"bracket":return function(t,r,n){return e=/(\[\])$/.exec(t),t=t.replace(/\[\]$/,""),e?void 0===n[t]?void(n[t]=[r]):void(n[t]=[].concat(n[t],r)):void(n[t]=r)};default:return function(t,e,r){if(void 0===r[t])return void(r[t]=e);r[t]=[].concat(r[t],e)}}}function a(t,e){return e.encode?e.strict?s(t):encodeURIComponent(t):t}function i(t){return Array.isArray(t)?t.sort():"object"==typeof t?i(Object.keys(t)).sort(function(t,e){return Number(t)-Number(e)}).map(function(e){return t[e]}):t}var s=r(580),u=r(6);e.extract=function(t){return t.split("?")[1]||""},e.parse=function(t,e){e=u({arrayFormat:"none"},e);var r=o(e),n=Object.create(null);return"string"!=typeof t?n:(t=t.trim().replace(/^(\?|#|&)/,""))?(t.split("&").forEach(function(t){var e=t.replace(/\+/g," ").split("="),o=e.shift(),a=e.length>0?e.join("="):void 0;a=void 0===a?null:decodeURIComponent(a),r(decodeURIComponent(o),a,n)}),Object.keys(n).sort().reduce(function(t,e){var r=n[e];return Boolean(r)&&"object"==typeof r&&!Array.isArray(r)?t[e]=i(r):t[e]=r,t},Object.create(null))):n},e.stringify=function(t,e){e=u({encode:!0,strict:!0,arrayFormat:"none"},e);var r=n(e);return t?Object.keys(t).sort().map(function(n){var o=t[n];if(void 0===o)return"";if(null===o)return a(n,e);if(Array.isArray(o)){var i=[];return o.slice().forEach(function(t){void 0!==t&&i.push(r(n,t,i.length))}),i.join("&")}return a(n,e)+"="+a(o,e)}).filter(function(t){return t.length>0}).join("&"):""}},580:function(t,e,r){"use strict";t.exports=function(t){return encodeURIComponent(t).replace(/[!'()*]/g,function(t){return"%"+t.charCodeAt(0).toString(16).toUpperCase()})}},792:function(t,e,r){"use strict";function n(t){return(0,u.default)("/wechatfans/getthirdpartinfo?limit=undefined&offset=undefined&alldata="+t,{method:"GET"})}function o(t){var e=(t-1)*f.PAGE_SIZE;return(0,u.default)("/wechatfans/getcloudconfig?limit="+f.PAGE_SIZE+"&offset="+e,{method:"GET"})}function a(){return(0,u.default)("/wechatfans/getcloudname",{method:"GET"})}function i(t,e,r){return(0,u.default)("/wechatfans/savecloudconfig?cloudid="+t+"&thirdpart="+e+"&typeThird="+r,{method:"GET"})}Object.defineProperty(e,"__esModule",{value:!0}),e.fetchsTh=n,e.fetchyun=o,e.fetchname=a,e.savename=i;var s=r(570),u=function(t){return t&&t.__esModule?t:{default:t}}(s),f=r(549)}});