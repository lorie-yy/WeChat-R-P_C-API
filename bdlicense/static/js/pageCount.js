$(document).ready(function () {
    var pageNum=9;  //每页显示的tr行数
    var index=1,oldIndex;      //页码，li标签里的数值，第一个'《'和最后一个'》'不计算在内;oldIndex表示原先的index值
    var $tr_len=Math.ceil(($("tr").length-1)/pageNum);  //总页数
    $(".xzy_ul").append('<li class="pageCode home_page">'+'首页'+'</li>');
    $(".xzy_ul").append('<li class="pageCode prev">'+'<'+'</li>');
    for(var m=1;m<=$tr_len;m++){
        $(".xzy_ul").append('<li class="pageCode">'+m+'</li>');
    }
    if($tr_len>5){
        $(".pageCode").slice(7,$tr_len+2).hide();
    }
    $(".xzy_ul").append('<li class="pageCode next">'+'>'+'</li>');
    $(".xzy_ul").append('<li class="pageCode trailer_page">'+'尾页'+'</li>');
//        动态添加li标签列表、鼠标移入变色
    $(".pageCode").css({'float':'left', 'text-align':'center', 'width':'42px', 'height':'32px', 'padding':'5px', 'background':'#f7f7f7', 'color':'dodgerblue','cursor':'pointer','border':'1px solid transparent'});
    $(".pageCode").hover(function () {
        $(this).css('border','1px solid lightgray');
    },function () {
        $(this).css('border','1px solid transparent');
    });
//        点击页码数字显示内容tr
    function pageCount(pageNum) {
        $("tr:not(tr:first)").css('display','none');
        for(var i=2;i<$(".pageCode").length-2;i++){
            (function (m) {
                $(".pageCode")[m].onclick=function () {
//                        $(document).scrollTop(0); //滚动条至顶端
                    index=parseInt(this.innerHTML);
                    xzy_skip();
                };
            })(i);
        }
//            第一页默认显示的tr
        $("tr").slice(1,pageNum+1).css('display','block').css('display','table-row');
    }
    pageCount(pageNum);
//        页码之间跳转的共有方法及样式函数
    function xzy_skip() {
        $(document).scrollTop(0);
        $("tr:not(tr:first)").css('display','none');
        $("tr").slice(pageNum*index-pageNum+1,pageNum*index+1).css('display','block').css('display','table-row');
        $(".pageList").val(index);
//            alert($tr_len +"AA"+index)
        if(index>=($tr_len-2) && $tr_len>5){
            oldIndex=index;
            index=$tr_len-2;
            $(".pageCode").slice(2,$tr_len+1).hide();
            $(".pageCode").slice(index-1,index+4).show();
            index=oldIndex;
        }else{
            $(".pageCode").slice(2,$tr_len+2).hide();
            $(".pageCode").slice(2,7).show();
        }
        $(".pageCode").css({'color':'dodgerblue','background':'#f7f7f7'});
        $(".pageCode")[index+1].style.color='white';
        $(".pageCode")[index+1].style.background='dodgerblue';
    }
//        首页尾页、上一页下一页效果
    $(".home_page").click(function () {
        index=1;
        xzy_skip();
    });
    $(".trailer_page").click(function () {
        index=$tr_len;
        xzy_skip();
    });
    $(".prev").click(function () {
        index--;
        if(index===0){ index=1; }
        xzy_skip();
    });
    $(".next").click(function () {
        index++;
        if(index===($tr_len+1)){ index=$tr_len; }
        xzy_skip();
    });
//        添加input输入框和button按钮
    $(".xzy_page").append('<input class="pageList" type="number" placeholder="页数" style="height: 30px;width: 60px;outline: medium;padding-left: 10px;border: none;border-bottom: 1px solid dodgerblue;text-align: center;position: relative;top: -11px"/>');
    $(".xzy_page").append('<button class="pageConfig" style="height: 32px;width: 60px;border: none;outline: medium;color: dodgerblue;background:#f7f7f7;cursor:pointer;position: relative;top: -11px">'+'确认'+'</button>');
//        点击确认显示输入数字的所在页面并判断所输入值的大小
    $(".pageConfig").click(function () {
        $(document).scrollTop(0);
        index=parseInt($(".pageList").val());
        if($(".pageList").val()<1){
            index=1;
            $(".pageList").val(index);
        }else if($(".pageList").val()>$tr_len){
            index=$tr_len;
            $(".pageList").val(index);
        }
        xzy_skip();
    });
    $(".pageConfig").hover(function () {
        $(this).css({'background':'dodgerblue','color':'white'});
    },function () {
        $(this).css({'background':'#f7f7f7','color':'dodgerblue'});
    });
    $(".pageCode")[2].style.color='white';
    $(".pageCode")[2].style.background='dodgerblue';
});
