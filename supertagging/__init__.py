__version_info__ = {
    'major': 0,
    'minor': 4,
    'micro': 10,
    'releaselevel': 'final',
    'serial': 0
}

def get_version():
    vers = ["%(major)i.%(minor)i" % __version_info__, ]

    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)

__version__ = get_version()

class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model more than once.
    """
    pass


registry = []


def register(model, tag_descriptor_attr='supertags',
             tagged_item_manager_attr='supertagged'):
    """
    Sets the given model class up for working with supertags.
    """

    from supertagging.managers import ModelTaggedItemManager, TagDescriptor

    if model in registry:
        raise AlreadyRegistered("The model '%s' has already been "
            "registered." % model._meta.object_name)
    if hasattr(model, tag_descriptor_attr):
        raise AttributeError("'%s' already has an attribute '%s'. You must "
            "provide a custom tag_descriptor_attr to register." % (
                model._meta.object_name,
                tag_descriptor_attr,
            )
        )
    if hasattr(model, tagged_item_manager_attr):
        raise AttributeError("'%s' already has an attribute '%s'. You must "
            "provide a custom tagged_item_manager_attr to register." % (
                model._meta.object_name,
                tagged_item_manager_attr,
            )
        )

    # Add tag descriptor
    setattr(model, tag_descriptor_attr, TagDescriptor())

    # Add custom manager
    ModelTaggedItemManager().contribute_to_class(model, tagged_item_manager_attr)

    # Finally register in registry
    registry.append(model)