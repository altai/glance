# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

from glance.common import exception


_BASE_SCHEMA_PROPERTIES = {
    'image': {
        'id': {
            'type': 'string',
            'description': 'An identifier for the image',
            'required': False,
            'maxLength': 36,
        },
        'name': {
            'type': 'string',
            'description': 'Descriptive name for the image',
            'required': True,
            'maxLength': 255,
        },
    },
    'access': {
        'tenant_id': {
          'type': 'string',
          'description': 'The tenant identifier',
          'required': True,
        },
        'can_share': {
          'type': 'boolean',
          'description': 'Ability of tenant to share with others',
          'required': True,
          'default': False,
        },
    },
}


class API(object):
    def __init__(self, base_properties=_BASE_SCHEMA_PROPERTIES):
        self.base_properties = base_properties
        self.schema_properties = copy.deepcopy(self.base_properties)

    def get_schema(self, name):
        return {
            'name': name,
            'properties': self.schema_properties[name],
        }

    def set_custom_schema_properties(self, schema_name, custom_properties):
        """Update the custom properties of a schema with those provided."""
        schema_properties = copy.deepcopy(self.base_properties[schema_name])

        # Ensure custom props aren't attempting to override base props
        base_keys = set(schema_properties.keys())
        custom_keys = set(custom_properties.keys())
        intersecting_keys = base_keys.intersection(custom_keys)
        conflicting_keys = [k for k in intersecting_keys
                            if schema_properties[k] != custom_properties[k]]
        if len(conflicting_keys) > 0:
            props = ', '.join(conflicting_keys)
            reason = _("custom properties (%(props)s) conflict "
                       "with base properties")
            raise exception.SchemaLoadError(reason=reason % {'props': props})

        schema_properties.update(copy.deepcopy(custom_properties))
        self.schema_properties[schema_name] = schema_properties
