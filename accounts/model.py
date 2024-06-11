from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from accounts.listeners import user_changed, profile_changed


class UserProfile(models.Model):
    # One2One filed would create a unique index
    # to make sure there is no other userProfile point to the same User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django has imageFiled, but it has so many problems
    # we would better not use it
    # FileField has the similar functionality
    avatar = models.FileField(null=True)
    # when a user is created, at the same time, would create a userProfile object
    # but user can not set it up immediately
    # so set null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)

"""
定义一个profile的property方法，植入到User 这个model里面去
这样当我们通过user 的一个实例化对象访问profile的时候，即user_instance.profile
就会在UserProfilUser中进行get_or_create来获取对应的profile的object
这种方法实际上是利用python的灵活性进行hack的方法
这样写方便我们通过user快速访问到对应的profile信息里面
instance level cache
"""
def get_profile(user):
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    # profile, _ = UserProfile.objects.get_or_create(user=user)
    profile = UserService.get_profile_through_cache(user_id=user.id)
    # 使用user对象的属性进行缓存cache。避免多次重复调用同一个user的profile
    # 对数据库进行重复查询
    setattr(user, '_cached_user_profile', profile)
    return profile


User.profile = property(get_profile)

pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)

