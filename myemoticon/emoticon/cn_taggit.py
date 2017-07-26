from unidecode import unidecode
from django.template.defaultfilters import slugify
from taggit.models import Tag, TaggedItem


class CnTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        return slugify(unidecode(self.name))[:128]


class CnTaggedItem(TaggedItem):
    class Meta:
        proxy = True
    
    @classmethod
    def tag_model(cls):
        return CnTag
