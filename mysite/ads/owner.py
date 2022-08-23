from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin


class OwnerListView(ListView):
    pass


class OwnerDetailView(DetailView):
    pass


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
