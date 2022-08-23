from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from .models import Ad, Comment, Favs
from .forms import CreateForm, CommentForm
from .owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime


class AdListView(OwnerListView):
    model = Ad
    template_name = 'ads/ad_list.html'

    def get(self, request):
        favorites = []
        if request.user.is_authenticated:
            favorites = request.user.favorite_ads.values_list('id', flat=True)

        strval = request.GET.get("search", False)
        if strval:
            query = Q(title__icontains=strval) | Q(text__icontains=strval)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]

        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'ad_list': ad_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"

    def get(self, request, pk):
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        ctx = {'ad': x, 'comment_form': comment_form, 'comments': comments}
        return render(request, self.template_name, ctx)


class AdCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        a = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=a)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])


@method_decorator(csrf_exempt, 'dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        a = get_object_or_404(Ad, id=pk)
        fav = Favs(user=request.user, ad=a)
        try:
            fav.save()
        except IntegrityError:  # In case of duplicate key
            pass

        return HttpResponse()


@method_decorator(csrf_exempt, 'dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        a = get_object_or_404(Ad, id=pk)
        try:
            fav = Favs.objects.get(user=request.user, ad=a).delete()
        except Favs.DoesNotExist:
            pass

        return HttpResponse()
