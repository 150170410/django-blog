from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as d_login, logout as d_logout
#import markdown


def post_list(request):
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date').reverse()
    except:
        posts = Post.objects.filter(published_date__lte=timezone.now()).filter(visiable__name='public').order_by('published_date').reverse()
    return pagination(request,posts)

def post_list_sort(request, sort_type):
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        if sort_type == 'date':
            posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date').reverse()
        elif sort_type == 'view':
            posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('views').reverse()
    except:
        if sort_type == 'date':
            posts = Post.objects.filter(published_date__lte=timezone.now()).filter(visiable__name='public').order_by('published_date').reverse()
        elif sort_type == 'view':
            posts = Post.objects.filter(published_date__lte=timezone.now()).filter(visiable__name='public').order_by('views').reverse()
    return pagination(request,posts)

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.comments = post.comment_set.all().filter().order_by('-created_time')
    post.increase_views()
    #post.text = markdown.markdown(post.text, extensions=['markdown.extensions.extra','markdown.extensions.codehilite','markdown.extensions.toc'])
    return render(request, 'blog/post_detail.html', {'post': post})

def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            try:
                post.author = request.user
            except ValueError:
                return HttpResponse('<h1>please login first</h1>')
            post.save()
            return redirect(post_detail, post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def create_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            try:
                post.author = request.user
            except ValueError:
                return HttpResponse('<h1>请先登陆</h1>')
            post.published_date = timezone.now()
            post.save()
            return redirect(post_detail, post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'blog/create_new.html', {'form': form})

def archives(request):
    all_category = []
    all_tag = []
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        date_list = Post.objects.dates('published_date', 'month', order='DESC')
        posts = Post.objects.all()
        for p in posts:
            if p.category.name not in all_category:
                all_category.append(p.category.name)
            for t in p.tag.all():
                if t.name not in all_tag:
                    all_tag.append(t.name)
    except:
        date_list = Post.objects.filter(visiable__name='public').dates('published_date', 'month', order='DESC')
        posts = Post.objects.filter(visiable__name='public')
        for p in posts:
            if p.category.name not in all_category:
                all_category.append(p.category.name)
            for t in p.tag.all():
                if t.name not in all_tag:
                    all_tag.append(t.name)
    all_category.sort()
    all_tag.sort()
    return render(request, 'blog/archives.html', context={'date_list': date_list, 'category_list': all_category, 'tag_list': all_tag})

def archives_date(request, year, month):
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        posts = Post.objects.filter(published_date__year=year,published_date__month=month).order_by('published_date').reverse()
    except:
        posts = Post.objects.filter(visiable__name='public').filter(published_date__year=year,published_date__month=month).order_by('published_date').reverse()
    return pagination(request,posts)

def archives_category(request, category_name):
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        posts = Post.objects.filter(published_date__lte=timezone.now()).filter(category__name=category_name).order_by('published_date').reverse()
    except:
        posts = Post.objects.filter(visiable__name='public').filter(published_date__lte=timezone.now()).filter(category__name=category_name).order_by('published_date').reverse()
    return pagination(request,posts)

def archives_tag(request, tag_name):
    try:
        login_user = request.user
        if str(login_user) == 'AnonymousUser':
            raise
        posts = Post.objects.filter(published_date__lte=timezone.now()).filter(tag__name=tag_name).order_by('published_date').reverse()
    except:
        posts = Post.objects.filter(visiable__name='public').filter(published_date__lte=timezone.now()).filter(tag__name=tag_name).order_by('published_date').reverse()
    return pagination(request,posts)

def pagination(request,filter_posts):
    paginator = Paginator(filter_posts, 5)
    page = request.GET.get('page',1)
    try:
        part_posts = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver first page.
        part_posts = paginator.page(1)
    except EmptyPage:
        #if page is out of range, deliver last page of results
        part_posts = paginator.page(paginator.num_pages)
    #return render(request, 'blog/post_list.html', {'posts':posts})
    return render(request, 'blog/post_list.html', {'posts':part_posts})

def about_site_me(request):
    return render(request, 'blog/about.html')

def about_me(request):
    import jieba
    import wordcloud
    import os

    wc_file_name = "./media/wordcloud/aboutme_wordcloud.png"
    if os.path.exists(wc_file_name):
        os.remove(wc_file_name)
    with open("./media/wordcloud/string_source.txt","r", encoding='UTF-8') as f:
        text = f.read()
    cut = jieba.cut(text)
    strings = ' '.join(cut)

    w = wordcloud.WordCloud(font_path = './media/wordcloud/simhei.ttf',width = 1000,height = 700,background_color = 'white')
    w.generate(strings)
    w.to_file(wc_file_name)
    return render(request, 'blog/about_me.html')

def about_site(request):
    return render(request, 'blog/about_site.html')

def do_login(request):
    if request.method == 'GET':
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/') 
        request.session['login_error'] = False
        user = request.user
        if user.is_authenticated:
            return redirect(reverse("post_list"))
        else:
            return render(request, 'blog/login.html')
    elif request.method == "POST":
        userName = request.POST['user-name']
        userPassword = request.POST['user-pw']
        user = authenticate(username=userName, password=userPassword)
        if user is not None: 
            if user.is_active:
                d_login(request, user)
                return redirect(request.session['login_from'])  # go back to page before login
            else:
                request.session['login_error'] = "未激活用户"
                return render(request,'blog/login.html',{'username':userName,'password':userPassword})
        else:
            request.session['login_error'] = "错误的用户名或密码"
            return render(request,'blog/login.html',{'username':userName,'password':userPassword})

def do_logout(request):
    d_logout(request)
    return redirect(reverse('post_list'))

def show_view_record(request):
    days = request.POST.get('day_period')
    #view_string = "<thead><tr><th scope='col'>#</th><th scope='col'>name1</th><th scope='col'>name2</th><th scope='col'>name3</th></tr></thead>"
    import codecs
    with codecs.open("/home/test/record_view/count_record_views.csv",encoding="utf8") as f:
        data = f.readlines()

    seq_sort = []
    start_flag = False
    start_seq = 0
    end_seq = 0
    for seq, line in enumerate(data):
        if len(line) > 1 and start_flag == False:
            start_seq = seq
            start_flag = True
        elif len(line) <= 1 and start_flag == True:
            end_seq = seq-1
            seq_sort.append((start_seq, end_seq))
            start_flag = False
    seq_sort.reverse()
    seq_sort = seq_sort[:5]

    temp_head_string = ""
    for number_list in seq_sort:
        temp_head_string += "<th scope='col'>%s</th>" % data[number_list[0]][:10]
    thead_string = "<thead><tr><th scope='col'>#</th>%s</tr></thead>" % temp_head_string

    recorded_post_ids = data[int(seq_sort[0][0]) + 1].strip().split(",")
    recorded_post_values = [1, 2, 3, 4, 5]
    for num in range(len(seq_sort)):
        title_view_dict = {}
        id_list = data[int(seq_sort[num][0]) + 1].strip().split(",")
        name_list = data[int(seq_sort[num][0]) + 2].strip().split(",")
        views_list = data[int(seq_sort[num][1])].strip().split(",")
        for id_num in range(len(id_list)):
            title_view_dict[id_list[id_num]] = {"title": name_list[id_num], "views": views_list[id_num]}
        recorded_post_values[num] = title_view_dict
    tbody_string = "<tbody></tbody>"
    for post_id in recorded_post_ids:
        temp_tbody_td_string = ""
        for value_id in range(len(recorded_post_values)):
            try:
                temp_tbody_td_string += "<td>%s</td>" % recorded_post_values[value_id][post_id]["views"]
            except:
                temp_tbody_td_string += "<td>no data</td>"
        temp_tbody_string = "<tr><th scope='row'>%s</th>%s</tr>" % (recorded_post_values[0][post_id]["title"],temp_tbody_td_string)
        tbody_string += temp_tbody_string

    view_string = thead_string + tbody_string
    return HttpResponse('{"status":"success", "view_string":"%s"}' % view_string, content_type='application/json')
