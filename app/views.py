"""
Definition of views.
"""
import os
from django.shortcuts import render
from django.http import HttpRequest , HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from app.models import book ,NeedBook, recommend 
from django.template import RequestContext
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail

from django import forms
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    email = forms.EmailField(label='e-mail',widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'e-mail'}))
    password1 = forms.CharField(label='Password',
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
    password2= forms.CharField(label='confirm',
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class InfForm(forms.Form):
     
    school = forms.CharField(max_length=128, error_messages={'required':u'学校不能为空', 'invalid':u'学校输入有误'})
    major = forms.CharField(max_length=128, error_messages={'required':u'专业不能为空', 'invalid':u'专业输入有误'})
    description = forms.CharField( max_length=512, error_messages={'required':u'该项不能为空', 'invalid':u'该项输入有误'},required=False)
    contact = forms.CharField(max_length=50, error_messages={'required':u'联系方式不能为空', 'invalid':u'联系方式输入有误'})
    
def get_recommends(data):#这个函数为以后升级功能提供接口，目前仅返回预览
    r1=recommend('sfdl','/detail?id=20','static/app/images/2.jpg')
    r2=recommend('dxwl','/detail?id=30','static/app/images/1.jpg')
    return [r1,r2,r1,r2,r1,r2]


def get_similar(id_item):#这个函数为以后升级功能提供接口，目前仅返回预览
    all_the_books=book.objects.all()
    sum=len(all_the_books)
    if sum>4:
        recent_books=(all_the_books)[sum-4:sum-1]
    else:
        recent_books=all_the_books
    return recent_books


def home(request):

    recommends=get_recommends(0)#未定义的data

    all_the_books=book.objects.all()
    sum=len(all_the_books)
    if sum>8:
        recent_books=(all_the_books)[sum-9:sum-1]
    else:
        recent_books=all_the_books
    return render(
        request,
        'app/index.html',
        {
            'recommends':recommends,
            'books':recent_books,
        }
    )
    
    
def search(request):#独立的搜索功能，实现单个关键字搜索
    if request.method=='POST':
       try:
            searchForm=request.POST
            keyword=searchForm.get('keyword')
            book_list_all = book.objects.filter(name_book__icontains=keyword)

            info='搜索结果'
            if len(book_list_all)==0:
                book_list_all=book.objects.all()
                info='没有找到！你还可以看看：'

            paginator = Paginator(book_list_all, 9)
            books = paginator.page(1)
            return render(
                    request,
                    'app/items.html',
                    {
                        'books': books,
                        'keyword':{'keyword':keyword},
                        'info':{'info':info}
                    }
                    )
       except:
           return HttpResponseRedirect('/')

    elif request.method=='GET':
        try:

            page = request.GET.get('page')
            keyword = request.GET.get('keyword')
            book_list_all = book.objects.filter(name_book__icontains=keyword)

            info="搜索结果"
            if len(book_list_all)==0:
                book_list_all=book.objects.all()
                info='没有找到！你还可以看看：'

            paginator = Paginator(book_list_all, 9)
            try:
                    books = paginator.page(page)
            except PageNotAnInteger:
                    books = paginator.page(1)
            except EmptyPage:
                    books = paginator.page(paginator.num_pages)
            return render(
                    request,
                    'app/items.html',
                    {
                        'books': books,
                        'keyword':{'keyword':keyword},
                        'info':{'info':info}
                    }
                    )
        except:
           return HttpResponseRedirect('/')
    else:
            return HttpResponseRedirect('/')

def detail(request):
    if request.method=="GET":
        try:
            id_item = request.GET.get('id')
            print( id_item)
            item = book.objects.get(id=str(id_item))
            print(item)
            similar=get_similar(id_item)
            print(similar)
            return render(
                request,
                'app/single.html',
                {
                    'item':item,
                    'similar':similar,
                }
            )
        except:
           return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'联系我们',
            'message':'在使用过程中如果遇到一些问题请及时反馈给我们，也欢迎提出你的意见和建议',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'关于',
            'message':'易书网使用说明',
            'year':datetime.now().year,
        }
    )


def register(request):#新的register，简化了代码
        if request.method=='POST':
            errors=[]
            form=request.POST

            try:
                username=form.get('UserName')
                email=form.get('EmailAddress')
                password1=form.get('Password')
            except:
                errors.append("Invalid Form")
                return render(request,"app/register.html",{'errors':form})

            
            filterResult=User.objects.filter(username=username)
            if len(filterResult)>0:
               errors.append("用户名已存在")
               return render(request, "app/register.html",{'errors':errors})

            #由于智能表单的存在，下面的检查代码实际上不需要了。但为了防止恶意表单攻击，依然保留。
            if (len(username)<4 or len(username)>30):
                errors.append("用户名长度不符合要求")
                return render(request, "app/register.html", { 'errors': errors})

            listsym=['!','@','#','$','%','^','&','*','(',')','-','+','=',',','.',';',':','[',']','{','}','|']
            for i in range(len(listsym)):
                if (listsym[i] in username):
                    errors.append("用户名包含特殊字符")
                    return render(request, "app/register.html", {'errors': errors})

            user = User.objects.create_user(username,email,password1)
            user.save()
            #登录前需要先验证
            newUser=auth.authenticate(username=username,password=password1)
            if newUser is not None:
                auth.login(request, newUser)
                return HttpResponseRedirect("/")
        else:
            return render(request, "app/register.html",)


class BookForm_1_dianyuan(forms.Form):
    class_choices = (
        ('高等数学（A）（1）', '高等数学（A）（1）'),
        ('线性代数（B类）', '线性代数（B类）'),
        ('离散数学', '离散数学'),
        ('程序设计思想与方法', '程序设计思想与方法'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_2_dianyuan(forms.Form):
    class_choices = (
        ('大学物理（A类）（1）', '大学物理（A类）（1）'),
('高等数学（A）（2）', '高等数学（A）（2）'),
('概率统计', '概率统计'),
('C++程序设计（A类）', 'C++程序设计（A类）'),
('大学物理实验（1）', '大学物理实验（1）'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_3_dianqi(forms.Form):
    class_choices = (
        ('大学物理（A类）（2）', '大学物理（A类）（2）'),
        ('基本电路理论', '基本电路理论'),
        ('数字电子技术', '数字电子技术'),
        ('数理方法', '数理方法'),
        ('大学物理实验（2）', '大学物理实验（2）'),
        ('基本电路实验', '基本电路实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_3_cekong(forms.Form):
    class_choices = (
        ('大学物理（A类）（2）', '大学物理（A类）（2）'),
        ('基本电路理论', '基本电路理论'),
        ('数字电子技术', '数字电子技术'),
        ('数理方法', '数理方法'),
        ('大学物理实验（2）', '大学物理实验（2）'),
        ('基本电路实验', '基本电路实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_3_zidonghua(forms.Form):
    class_choices = (
        ('大学物理（A类）（2）', '大学物理（A类）（2）'),
        ('基本电路理论', '基本电路理论'),
        ('数字电子技术', '数字电子技术'),
        ('数理方法', '数理方法'),
        ('大学物理实验（2）', '大学物理实验（2）'),
        ('基本电路实验', '基本电路实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_dianqi(forms.Form):
    class_choices = (
        ('模拟电子技术', '模拟电子技术'),
        ('嵌入式系统原理与实验（A类）', '嵌入式系统原理与实验（A类）'),
        ('信号与系统（B类)', '信号与系统（B类）'),
        ('电磁场', '电磁场'),
        ('电子技术实验', '电子技术实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_cekong(forms.Form):
    class_choices = (
        ('模拟电子技术', '模拟电子技术'),
        ('嵌入式系统原理与实验（A类）', '嵌入式系统原理与实验（A类）'),
        ('信号与系统（B类)', '信号与系统（B类）'),
        ('电子技术实验', '电子技术实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_zidonghua(forms.Form):
    class_choices = (
        ('模拟电子技术', '模拟电子技术'),
        ('嵌入式系统原理与实验（A类）', '嵌入式系统原理与实验（A类）'),
        ('信号与系统（B类)', '信号与系统（B类）'),
        ('电子技术实验', '电子技术实验'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_5_dianqi(forms.Form):
    class_choices = (
        ('自动控制原理B', '自动控制原理B'),
        ('电力电子技术基础', '电力电子技术基础'),
        ('电机学', '电机学'),
        ('电气工程基础（1）', '电气工程基础（1）'),
        ('数字信号处理（B类）', '数字信号处理（B类）'),
        ('数据库（C类）', '数据库（C类）'),
        ('软件工程（C类）', '软件工程（C类）'),
        ('计算机通讯与网络', '计算机通讯与网络'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_5_cekong(forms.Form):
    class_choices = (
        ('电磁场', '电磁场'),
        ('自动控制原理B', '自动控制原理B'),
        ('测试与控制电路', '测试与控制电路'),
        ('传感器原理', '传感器原理'),
        ('精密仪器设计（1）', '精密仪器设计（1）'),
        ('工程力学', '工程力学'),
        ('现代图学', '现代图学'),
        ('可靠性设计', '可靠性设计'),
        ('工业测控技术与系统', '工业测控技术与系统'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_5_zidonghua(forms.Form):
    class_choices = (
        ('模式识别导论', '模式识别导论'),
        ('数字图像处理基础', '数字图像处理基础'),
        ('数字信号处理（A类）', '数字信号处理（A类）'),
        ('自动化仪表', '自动化仪表'),
        ('电力电子技术', '电力电子技术'),
        ('自动控制原理A', '自动控制原理A'),
        ('机器人学', '机器人学'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_dianqi(forms.Form):
    class_choices = (
        ('电气工程基础（2）', '电气工程基础（2）'),
        ('电力系统继电保护', '电力系统继电保护'),
        ('电力系统自动化', '电力系统自动化'),
        ('电力系统暂态分析', '电力系统暂态分析'),
        ('电机控制技术', '电机控制技术'),
        ('电气与电子测量技术', '电气与电子测量技术'),
        ('DSP实践', 'DSP实践'),
        ('可编程控制器原理及应用', '可编程控制器原理及应用'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_cekong(forms.Form):
    class_choices = (
        ('检测技术A', '检测技术A'),
        ('精密仪器设计（2）', '精密仪器设计（2）'),
        ('仪器总线与虚拟仪器', '仪器总线与虚拟仪器'),
        ('误差理论与数据处理', '误差理论与数据处理'),
        ('单片机与嵌入式仪器', '单片机与嵌入式仪器'),
        ('数字信号处理', '数字信号处理'),
        ('生物医学信息检测', '生物医学信息检测'),
        ('机器人技术基础', '机器人技术基础'),
        ('电子测量技术与仪器', '电子测量技术与仪器'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_zidonghua(forms.Form):
    class_choices = (
        ('检测技术B', '检测技术B'),
        ('数据结构B', '数据结构B'),
        ('非线性系统', '非线性系统'),
        ('现代控制理论（B类）', '现代控制理论（B类）'),
        ('过程控制系统', '过程控制系统'),
        ('运动控制系统', '运动控制系统'),
        ('计算机控制技术', '计算机控制技术'),
        ('IT项目管理', 'IT项目管理'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_dianqi(forms.Form):
    class_choices = (
        ('电磁场数值计算', '电磁场数值计算'),
        ('微机控制技术', '微机控制技术'),
        ('现代电气技术讲座', '现代电气技术讲座'),
        ('介质工程与光纤技术', '介质工程与光纤技术'),
        ('电机设计', '电机设计'),
        ('电力系统潮流计算机分析', '电力系统潮流计算机分析'),
        ('电力系统优化运行与市场化', '电力系统优化运行与市场化'),
        ('电气设备的绝缘检测与故障诊断', '电气设备的绝缘检测与故障诊断'),
        ('电磁兼容技术', '电磁兼容技术'),
        ('电网数字化保护控制技术及应用', '电网数字化保护控制技术及应用'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_cekong(forms.Form):
    class_choices = (
        ('通信原理（B类）', '通信原理（B类）'),
        ('数据结构B', '数据结构B'),
        ('现代控制理论（A类）', '现代控制理论（A类）'),
        ('图像检测技术基础（中英文）', '图像检测技术基础（中英文）'),
        ('全球导航卫星系统（双语）', '全球导航卫星系统（双语）'),
        ('无损检测', '无损检测'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_zidonghua(forms.Form):
    class_choices = (
        ('操作系统（A类）', '操作系统（A类）'),
        ('金融建模及其R软件实例分析', '金融建模及其R软件实例分析'),
        ('系统设计中的人为因素', '系统设计中的人为因素'),
        ('控制系统仿真', '控制系统仿真'),
        ('单片机系统设计', '单片机系统设计'),
        ('数字程序控制系统', '数字程序控制系统'),
        ('数字系统设计技术', '数字系统设计技术'),
        ('传感器网络', '传感器网络'),
        ('线性规划与非线性规划', '线性规划与非线性规划'),
        ('JAVA语言', 'JAVA语言'),
        ('数据库原理与应用', '数据库原理与应用'),
        ('计算机网络（A类）', '计算机网络（A类）'),
        ('系统辨识基础', '系统辨识基础'),
        ('先进控制技术讲座', '先进控制技术讲座'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )
    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()








class BookForm_3_xinan(forms.Form):
    class_choices = (
        ('数据结构与算法','数据结构与算法'),
        ('基本电路理论','基本电路理论'),
        ('数字电子技术','数字电子技术'),
        ('软件工程','软件工程'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_xinan(forms.Form):
    class_choices = (
        ('模拟电子技术','模拟电子技术'),
('信号与系统','信号与系统'),
('数据库原理','数据库原理'),
('信息安全的数学基础（1）','信息安全的数学基础（1）'),
('计算机组成与系统结构','计算机组成与系统结构'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_5_xinan(forms.Form):
    class_choices=(('编译原理（C类）','编译原理（C类）'),
('计算机通信网络(A类)','计算机通信网络(A类)'),
('数字信号处理（E类）','数字信号处理（E类）'),
('数字系统设计','数字系统设计'),
('信息论与编码','信息论与编码'),
('信息安全的数学基础（2)','信息安全的数学基础（2)'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_6_xinan(forms.Form):
    class_choices=(('操作系统（B类)','操作系统（B类)'),
('嵌入式系统原理与应用','嵌入式系统原理与应用'),
('Windows安全原理与技术','Windows安全原理与技术'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_xinan(forms.Form):
    class_choices=(('Internet安全协议与分析','Internet安全协议与分析'),
('现代密码学','现代密码学'),
                   )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()






class BookForm_3_ruanyuan(forms.Form):
    class_choices = (
        ('计算机系统基础（1）','计算机系统基础（1）'),
('算法原理','算法原理'),
('电路系统综合','电路系统综合'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_ruanyuan(forms.Form):
    class_choices = (
       ('计算机系统基础（2）','计算机系统基础（2）'),
('数据库原理与技术','数据库原理与技术'),
('软件工程导论','软件工程导论'),
('Web开发技术','Web开发技术'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_5_ruanyuan(forms.Form):
    class_choices=(('计算机系统工程','计算机系统工程'),
('软件测试','软件测试'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_6_ruanyuan(forms.Form):
    class_choices=(('计算机体系结构','计算机体系结构'),
('分布式系统','分布式系统'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()



class BookForm_3_jisuanji(forms.Form):
    class_choices = (
        ('电路系统综合','电路系统综合'),
('数据结构A','数据结构A')
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_jisuanji(forms.Form):
    class_choices = (
      ('操作系统（D类）','操作系统（D类）'),
('算法与复杂性','算法与复杂性'),
('计算机系统结构（A类)','计算机系统结构（A类)'),
('计算机科学中的数学基础','计算机科学中的数学基础')
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_5_jisuanji(forms.Form):
    class_choices=(('人工智能（B类）','人工智能（B类）'),
('计算理论','计算理论'))
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_6_jisuanji(forms.Form):
    class_choices=(('数据科学基础','数据科学基础'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_jisuanji(forms.Form):
    class_choices=(('数据挖掘','数据挖掘'),
                   ('大数据处理','大数据处理'),
                   ('智能语音技术', '智能语音技术'),
                   ('多核计算与并行处理', '多核计算与并行处理'),
                   ('并行与分布式程序设计', '并行与分布式程序设计'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()




class BookForm_3_weidianzi(forms.Form):
    class_choices=(
('大学物理（A类）（2）','大学物理（A类）（2）'),
('基本电路理论','基本电路理论'),
('数字电子技术','数字电子技术'),
('数理方法','数理方法'),
('数据结构B','数据结构B'),
)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_weidianzi(forms.Form):
    class_choices=(('嵌入式系统原理与实验（A类）','嵌入式系统原理与实验（A类）'),
('信号与系统（A类）','信号与系统（A类）'),
('软件工程','软件工程'),
('半导体物理与器件','半导体物理与器件'),
('数字集成电路设计','数字集成电路设计'),)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


class BookForm_5_weidianzi(forms.Form):
    class_choices=(
('数字信号处理','数字信号处理'),
('电磁场','数字信号处理'),
('算法原理','数字信号处理'),
('操作系统（E类）','操作系统（E类）'),
('信息论基础','信息论基础'),
('自动控制原理B','自动控制原理B'),
('近代物理（电子类）','近代物理（电子类）'),
('模拟集成电路设计','模拟集成电路设计'),
('VLSI数字通信原理','VLSI数字通信原理'),
)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_weidianzi(forms.Form):
    class_choices=(
('混合信号集成电路设计引论','混合信号集成电路设计引论'),
('集成电路测试基础','集成电路测试基础'),
('先进数字系统芯片设计','先进数字系统芯片设计'),
('设计自动化引论','设计自动化引论'),
)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()



class BookForm_7_weidianzi(forms.Form):
    class_choices=(
('射频集成电路设计引论','射频集成电路设计引论'),
('多媒体原理与技术','多媒体原理与技术'),
('光电原理与传感器应用','光电原理与传感器应用'),
)

    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_3_dianke(forms.Form):
    class_choices=(
('大学物理（A类）（2）','大学物理（A类）（2）'),
('基本电路理论','基本电路理论'),
('数字电子技术','数字电子技术'),
('数理方法','数理方法'),
('数据结构B','数据结构B'),
    )
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_dianke(forms.Form):
    class_choices=(
('信号与系统（A类）','信号与系统（A类）'),
('模拟电子技术','模拟电子技术'),
('嵌入式系统原理与实验（A类）','嵌入式系统原理与实验（A类）'),
('硬件描述语言与系统仿真','硬件描述语言与系统仿真'),
('电子信息领域前沿技术（工程）探究','电子信息领域前沿技术（工程）探究'),
('电磁场（A类）','电磁场（A类）'),
)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_5_dianke(forms.Form):
    class_choices=(
('近代物理（电子类）','近代物理（电子类）'),
('数字信号处理','数字信号处理'),
('光纤通信概论','光纤通信概论'),
('通信原理与实验','通信原理与实验'),
('微波技术','微波技术'),
('半导体物理与器件','半导体物理与器件'),
('机器学习与视频内容理解','机器学习与视频内容理解'),
('网络安全导论','网络安全导论'),
('视觉定位与感知','视觉定位与感知'),
('空时无线信道导论','空时无线信道导论'),
('光电子器件','光电子器件'),
('信息光子学','信息光子学'),
('现代天线理论与技术','现代天线理论与技术'),
)
    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_dianke(forms.Form):
    class_choices=(
('光电子学基础','光电子学基础'),
('通信基本电路与实验','通信基本电路与实验'),
('计算通信理论','计算通信理论'),
('激光原理与技术','激光原理与技术'),
('多媒体通信系统与实现','多媒体通信系统与实现'),
('信息论基础','信息论基础'),
('无线通信新技术与实践','无线通信新技术与实践'),
('无线组网技术','无线组网技术'),
('新型光通信系统','新型光通信系统'),
('大数据通信网络模型和算法','大数据通信网络模型和算法'),
('机器学习','机器学习'),
('网络安全管理技术','网络安全管理技术'),
('现代感知技术','现代感知技术'),
('微波遥感技术','微波遥感技术'),
('射频电路设计','射频电路设计'),
('电子设计自动化','电子设计自动化'),
('光电子集成技术与工艺','光电子集成技术与工艺'),
('光电显示技术','光电显示技术'),
('光量子学基础','光量子学基础'),
('传输与交换光子学','传输与交换光子学'),
('智能天线与多维阵列','智能天线与多维阵列'),
('超材料技术及多模传感器','超材料技术及多模传感器'),
)

    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_7_dianke(forms.Form):
    class_choices=(
('大数据处理','	大数据处理'),
)

    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_3_xingong(forms.Form):
    class_choices=(
('大学物理（A类）（2）','大学物理（A类）（2）'),
('基本电路理论','基本电路理论'),
('数字电子技术','数字电子技术'),
('数理方法','数理方法'),
('数据结构B','数据结构B'),
)

    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_4_xingong(forms.Form):
        class_choices = (
('信号与系统（A类）','信号与系统（A类）'),
('模拟电子技术','模拟电子技术'),
('嵌入式系统原理与实验（A类）','嵌入式系统原理与实验（A类）'),
('硬件描述语言与系统仿真','硬件描述语言与系统仿真'),
('电子信息领域前沿技术（工程）探究','电子信息领域前沿技术（工程）探究'),
('电磁场（A类）','电磁场（A类）'),
)

        name_book = forms.ChoiceField(choices=class_choices)
        discount_choices = (
            ('1', '一折'),
            ('2', '二折'),
            ('3', '三折'),
        )

        discount_book = forms.ChoiceField(choices=discount_choices)
        photo_book = forms.FileField()

class BookForm_5_xingong(forms.Form):
    class_choices=(
('数字信号处理','数字信号处理'),
('通信原理与实验','通信原理与实验'),
('微波技术','微波技术'),
('光纤通信概论','光纤通信概论'),
('图像处理与通信','图像处理与通信'),
('操作系统','操作系统'),
('机器学习与视频内容理解','机器学习与视频内容理解'),
)

    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()

class BookForm_6_xingong(forms.Form):
    class_choices=(
('通信基本电路与实验','通信基本电路与实验'),
('无线通信原理与移动网络','无线通信原理与移动网络'),
('信息论基础','信息论基础'),
)


    name_book = forms.ChoiceField(choices=class_choices)
    discount_choices =(
        ('1', '一折'),
        ('2', '二折'),
        ('3', '三折'),
    )

    discount_book = forms.ChoiceField(choices=discount_choices)
    photo_book = forms.FileField()


def upload_book(request,book_grade,book_major):
    book_grade_dict={'1':'大一上','2':'大一下','3':'大二上','4':'大二下','5':'大三上','6':'大三下','7':'大四上'}
    book_major_dict={'dianyuan':'电院大平台','xinan':'信安','ruanyuan':'软院','jisuanji':'计算机','dianqi':'电气','cekong':'测控','zidonghua':'自动化','weidianzi':'微电子','dianke':'电科','xingong':'信工'}
    book_form_dict ={'1dianyuan':BookForm_1_dianyuan,'2dianyuan':BookForm_2_dianyuan,'3dianqi':BookForm_3_dianqi,'3cekong':BookForm_3_cekong,'3zidonghua':BookForm_3_zidonghua,
                     '4dianqi':BookForm_4_dianqi,'4cekong':BookForm_4_cekong,'4zidonghua':BookForm_4_zidonghua,
                     '5dianqi': BookForm_5_dianqi, '5cekong': BookForm_5_cekong, '5zidonghua': BookForm_5_zidonghua,
                     '6dianqi': BookForm_6_dianqi, '6cekong': BookForm_6_cekong, '6zidonghua': BookForm_6_zidonghua,
                     '7dianqi': BookForm_7_dianqi, '7cekong': BookForm_6_cekong, '7zidonghua': BookForm_7_zidonghua,
                     '3xinan':BookForm_3_xinan,'4xinan':BookForm_4_xinan,'5xinan':BookForm_5_xinan,'6xinan':BookForm_6_xinan,'7xinan':BookForm_7_xinan,
                    '3ruanyuan':BookForm_3_ruanyuan,'4ruanyuan':BookForm_4_ruanyuan,'5ruanyuan':BookForm_5_ruanyuan,'6ruanyuan':BookForm_6_ruanyuan,
                     '3jisuanji':BookForm_3_jisuanji,'4jisuanji':BookForm_4_jisuanji,'5jisuanji':BookForm_5_jisuanji,'6jisuanji':BookForm_6_jisuanji,'7jisuanji':BookForm_7_jisuanji,
                     '3weidianzi':BookForm_3_weidianzi,'4weidianzi':BookForm_4_weidianzi,'5weidianzi':BookForm_5_weidianzi,'6weidianzi':BookForm_6_weidianzi,'7weidianzi':BookForm_7_weidianzi,
                     '3dianke': BookForm_3_dianke,'4dianke': BookForm_4_dianke,'5dianke': BookForm_5_dianke,'6dianke': BookForm_6_dianke,'7dianke': BookForm_7_dianke,
                     '3xingong': BookForm_3_xingong,'4xingong': BookForm_4_xingong, '5xingong': BookForm_5_xingong,'6xingong': BookForm_6_xingong
                    }
    book_form_dict_key = book_grade+book_major
    BookForm = book_form_dict[book_form_dict_key]
    if request.user.is_authenticated:
        if request.method == 'POST':
            book_form = BookForm(request.POST, request.FILES)
            if book_form.is_valid():
                name = book_form.cleaned_data['name_book']
                grade =book_grade_dict[book_grade]
                discount = book_form.cleaned_data['discount_book']
                major = book_major_dict[book_major]
                photo =book_form.cleaned_data['photo_book']
                # acquire courrent user
                user = request.user
                book = user.book_set.create(name_book=name, grade_book=grade, discount_book=discount, major_book=major,
                                            photo_book=photo)
                book.save()
                #发送邮件
                need_book_send_eamil(name , book.id)
                return HttpResponseRedirect('/user_book_detail')
            else:
                book_form = BookForm()
                return HttpResponseRedirect('/upload_book')
        else:
            book_form = BookForm()
            return render(request, "app/upload_book.html", {'book_form': book_form,'title':'发布旧书','year':datetime.now().year,'grade':book_grade_dict[book_grade],'major':book_major_dict[book_major]})
    else:
        return HttpResponseRedirect('/login')


def need_book_send_eamil(book_name,id):
    book_list = NeedBook.objects.filter(need_book_name = book_name)
    if book_list:
        needBook= book_list[0]
        name = needBook.need_book_name
        user = needBook.master
        email = user.email
        needBook.delete()
        id = str(id)

        message = str(user) + "发布了你预约的" +name +"这是这本书的详情请及时查看"+"http://yishu.prowu.cn/"+id
        send_mail('易书网', message, 'yishuwang2016@163.com',
            [email],fail_silently=False, )



def upload_book_choice(request):
    if request.user.is_authenticated:
        return render(request,"app/upload_book_choice.html")
    else:
        return HttpResponseRedirect('/login')

def user_book_detail(request):
    if request.user.is_authenticated:
        user = request.user
        upoladed_book = user.book_set.all()
        # modles里面类的名称要变成小写NeedBook->needbook
        need_book = user.needbook_set.all()
        context = {'uploaded_book_list':upoladed_book,
                   'need_book_list': need_book,
                   'title': '我的书籍',
                   'year': datetime.now().year,
                   }
        return render(request, 'app/user_book_detail.html', context)
    else:
        return HttpResponseRedirect('/login')

#通过传递参数book_id 来达到删除书的目的
def delete_book(request,book_id):
    book_id = book_id
    if request.user.is_authenticated:
        user = request.user
        book = user.book_set.get(id=book_id)
        current_path = os.path.abspath('.')
        path =current_path+'/media/'+str(book.photo_book)
        book.delete()
        os.remove(path)
    else:
        return HttpResponseRedirect('/login')
    return HttpResponseRedirect('/user_book_detail')

class search_form(forms.Form):
    keyword = forms.CharField(max_length=50)
    
def public_inf(request, c_user):
    if request.user.is_authenticated:
        if request.method == 'GET':
            target_user = User.objects.filter(username = c_user)
            if len(target_user)==1:
                return render(request, "app/public_inf.html", {"target_user": target_user[0],})
    return HttpResponseRedirect("/")

def personal_inf(request,c_user):
    origin= request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated and request.user.username == c_user:
        profile = request.user.userprofile
        if request.method=='POST': 
            form=InfForm(request.POST)

            if not form.is_valid():
               return render(request, "app/personal_inf.html",{'form':form,'title':'个人信息','year':datetime.now().year,})
            school = form.cleaned_data['school']
            major = form.cleaned_data['major']
            description= form.cleaned_data['description']
            contact = form.cleaned_data['contact']
        
            profile.school = school
            profile.major = major
            profile.description = description
            profile.contact = contact
            profile.save()
            return HttpResponseRedirect('/public_inf/'+str(request.user.username))
        else:
            form =InfForm()
            return render(request, "app/personal_inf.html",{'form':form,'title':'个人信息','year':datetime.now().year,})
    return HttpResponseRedirect("/")



def delete_need_book(request,book_id):
    book_id = book_id
    if request.user.is_authenticated:
        user = request.user
        book = user.needbook_set.filter(id=book_id)
        book.delete()
    else:
        return HttpResponseRedirect('/login')
    return HttpResponseRedirect('/user_book_detail')

class NeedBookForm(forms.Form):
    need_book_name = forms.CharField(max_length=50)

#目前有个小bug，可能会有预约两次的情况出现
def need_book(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            need_book_form = NeedBookForm(request.POST)
            if need_book_form.is_valid():
                name = need_book_form.cleaned_data['need_book_name']
                # acquire courrent user
                user = request.user
                need_book = NeedBook(master=user,need_book_name=name)
                need_book.save()
                return HttpResponseRedirect('/user_book_detail')
            else:
                need_book_form = NeedBookForm()
                return HttpResponseRedirect('/need_book')
        else:
            need_book_form = NeedBookForm()
            return render(request, "app/need_book.html", {'book_form': need_book_form,'title':'预约书','year':datetime.now().year})
    else:
        return HttpResponseRedirect('/login')


def book_detail(request,book_id):
    #filter return quseryset
    #get return the book object
    BOOK= book.objects.filter(id=book_id)
    return render(
        request,
        'app/book_detail.html',
        {
            'title':'书籍详情',
            'year':datetime.now().year,
            'book':BOOK,
        }
    )

