from django.db import models


class SomeModel(models.Model):
    name = models.CharField(max_length=200, verbose_name='Чтоб было')

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ('pk',)

    def __str__(self):
        return self.name
