/**
 * Created by gabi on 4/05/16.
 */
/**
 * Execute the user's code.
 * Just a quick and dirty eval.  No checks for infinite loops, etc.
 */

var saveAs=saveAs||(function(h){
    "use strict";
    var r=h.document,l=function(){
      return h.URL||h.webkitURL||h},e=h.URL||h.webkitURL||h,
        n=r.createElementNS("http://www.w3.org/1999/xhtml","a"),
        g="download" in n,
        j=function(t){
          var s=r.createEvent("MouseEvents");
          s.initMouseEvent("click",true,false,h,0,0,0,0,0,false,false,false,false,0,null);
          return t.dispatchEvent(s)
        },
        o=h.webkitRequestFileSystem,
        p=h.requestFileSystem||o||h.mozRequestFileSystem,
        m=function(s){
          (h.setImmediate||h.setTimeout)(function(){
            throw s},0)
        },
        c="application/octet-stream",
        k=0,b=[],
        i=function(){
          var t=b.length;while(t--){
            var s=b[t];
            if(typeof s==="string"){
              e.revokeObjectURL(s)}else{s.remove()
            }}b.length=0},
        q=function(t,s,w){
          s=[].concat(s);
          var v=s.length;
          while(v--){
            var x=t["on"+s[v]];
            if(typeof x==="function"){
              try{x.call(t,w||t)}
              catch(u){m(u)}}}},
        f=function(t,u){
          var v=this,B=t.type,E=false,x,w,
              s=function(){
                var F=l().createObjectURL(t);
                b.push(F);
                return F
              },
              A=function(){
                q(v,"writestart progress write writeend".split(" "))
              },
              D=function(){
                if(E||!x){
                  x=s(t)}w.location.href=x;v.readyState=v.DONE;A()
              },z=function(F){
            return function(){
              if(v.readyState!==v.DONE){
                return F.apply(this,arguments)}
            }
          },
              y={create:true,exclusive:false},
              C;v.readyState=v.INIT;
          if(!u){u="download"}if(g){
            x=s(t);
            n.href=x;
            n.download=u;
            if(j(n)){
              v.readyState=v.DONE;
              A();
              return
            }
          }
          if(h.chrome&&B&&B!==c){
            C=t.slice||t.webkitSlice;
            t=C.call(t,0,t.size,c);
            E=true
          }
          if(o&&u!=="download"){
            u+=".download"
          }
          if(B===c||o){
            w=h
          }
          else{
            w=h.open()
          }
          if(!p){
            D();
            return
          }
          k+=t.size;
          p(h.TEMPORARY,k,z(function(F){
            F.root.getDirectory("saved",y,z(function(G){
              var H=function(){
                G.getFile(u,y,z(function(I){I.createWriter(z(
                    function(J){J.onwriteend=function(K){
                      w.location.href=I.toURL();
                      b.push(I);
                      v.readyState=v.DONE;
                      q(v,"writeend",K)};
                      J.onerror=function(){
                        var K=J.error;
                        if(K.code!==K.ABORT_ERR){D()}
                      };"writestart progress write abort".split(" ").forEach(function(K){
                        J["on"+K]=v["on"+K]
                      });
                      J.write(t);
                      v.abort=function(){
                        J.abort();
                        v.readyState=v.DONE};
                      v.readyState=v.WRITING
                    }),D)}),D)};
              G.getFile(u,{create:false},z(function(I){
                I.remove();
                H()}),
                  z(function(I){if(I.code===I.NOT_FOUND_ERR){H()
                  }
                  else{
                    D()}
                  }))}),
                D)}),
              D)},d=f.prototype,a=function(s,t){
      return new f(s,t)};
    d.abort=function(){
      var s=this;
      s.readyState=s.DONE;
      q(s,"abort")};
    d.readyState=d.INIT=0;
    d.WRITING=1;
    d.DONE=2;
    d.error=d.onwritestart=d.onprogress=d.onwrite=d.onabort=d.onerror=d.onwriteend=null;
    h.addEventListener("unload",i,false);
    return a}(self));


/**
 * Backup code blocks to localStorage.
 */
function backup_blocks() {
  if ('localStorage' in window) {
    var xml = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
    window.localStorage.setItem('arduino', Blockly.Xml.domToText(xml));
  }
}

/**
 * Restore code blocks from localStorage.
 */
function restore_blocks() {
  if ('localStorage' in window && window.localStorage.arduino) {
    var xml = Blockly.Xml.textToDom(window.localStorage.arduino);
    Blockly.Xml.domToWorkspace(Blockly.mainWorkspace, xml);
  }
}

/**
 * Save blocks to local file.
 * better include Blob and FileSaver for browser compatibility
 */
function save() {
  var xml = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
  var data = Blockly.Xml.domToText(xml);

  // Store data in blob.
  // var builder = new BlobBuilder();
  // builder.append(data);
  // saveAs(builder.getBlob('text/plain;charset=utf-8'), 'blockduino.xml');
  console.log("saving blob");
  var blob = new Blob([data], {type: 'text/xml'});
  saveAs(blob, 'ardublocks.xml');
}

/**
 * Load blocks from local file.
 */
function load(event) {
  var files = event.target.files;
  // Only allow uploading one file.
  if (files.length != 1) {
    return;
  }

  // FileReader
  var reader = new FileReader();
  reader.onloadend = function(event) {
    var target = event.target;
    // 2 == FileReader.DONE
    if (target.readyState == 2) {
      try {
        var xml = Blockly.Xml.textToDom(target.result);
      } catch (e) {
        alert('Error parsing XML:\n' + e);
        return;
      }
      var count = Blockly.mainWorkspace.getAllBlocks().length;
      if (count && confirm('Replace existing blocks?\n"Cancel" will merge.')) {
        Blockly.mainWorkspace.clear();
      }
      Blockly.Xml.domToWorkspace(Blockly.mainWorkspace, xml);
    }
    // Reset value of input after loading because Chrome will not fire
    // a 'change' event if the same file is loaded again.
    document.getElementById('load').value = '';
  };
  reader.readAsText(files[0]);
}

/**
 * Discard all blocks from the workspace.
 */
function discard() {
  var count = Blockly.mainWorkspace.getAllBlocks().length;
  if (count < 2 || window.confirm('Delete all ' + count + ' blocks?')) {
    Blockly.mainWorkspace.clear();
    renderContent();
  }
}

/*
 * auto save and restore blocks
 */
function auto_save_and_restore_blocks() {
  // Restore saved blocks in a separate thread so that subsequent
  // initialization is not affected from a failed load.
  window.setTimeout(restore_blocks, 0);
  // Hook a save function onto unload.
  bindEvent(window, 'unload', backup_blocks);
  tabClick('tab_' + selected);

  // Init load event.
  var loadInput = document.getElementById('load');
  console.log(loadInput);
  loadInput.addEventListener('change', load, false);
  document.getElementById('fakeload').onclick = function() {
    console.log('fakeload clicked');
    loadInput.click();
  };
}

var loadInput = document.getElementById('load');
console.log(loadInput);
loadInput.addEventListener('change', load, false);
document.getElementById('fakeload').onclick = function() {
  console.log('fakeload clicked');
  loadInput.click();
};
/**
 * Bind an event to a function call.
 * @param {!Element} element Element upon which to listen.
 * @param {string} name Event name to listen to (e.g. 'mousedown').
 * @param {!Function} func Function to call when event is triggered.
 *     W3 browsers will call the function with the event object as a parameter,
 *     MSIE will not.
 */
function bindEvent(element, name, func) {
  if (element.addEventListener) {  // W3C
    element.addEventListener(name, func, false);
  } else if (element.attachEvent) {  // IE
    element.attachEvent('on' + name, func);
  }
}

