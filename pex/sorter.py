# Copyright 2015 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import

from pex.package import EggPackage, SourcePackage, WheelPackage


class Sorter(object):
  DEFAULT_PACKAGE_PRECEDENCE = (
      WheelPackage,
      EggPackage,
      SourcePackage,
  )

  @classmethod
  def package_type_precedence(cls, package, precedence=DEFAULT_PACKAGE_PRECEDENCE):
    for rank, package_type in enumerate(reversed(precedence)):
      if isinstance(package, package_type):
        return rank
    # If we do not recognize the package, it gets lowest precedence
    return -1

  @classmethod
  def package_platform_tag_precedence(cls, package):
    # Give all non 'any' tags higher precedence
    supported_tags = package.supported_tags or []
    platforms = set([tags[2] for tags in supported_tags])
    if 'any' in platforms:
      return -1
    else:
      return 0

  @classmethod
  def package_precedence(cls, package, precedence=DEFAULT_PACKAGE_PRECEDENCE):
    return (
        package.version,  # highest version
        cls.package_type_precedence(package, precedence=precedence),  # type preference
        cls.package_platform_tag_precedence(package),  # platform preference
        package.local)  # prefer not fetching over the wire

  def __init__(self, precedence=None):
    self._precedence = precedence or self.DEFAULT_PACKAGE_PRECEDENCE

  # return sorted list of (possibly filtered) packages from the list
  def sort(self, packages, filter=True):
    key = lambda package: self.package_precedence(package, self._precedence)
    return [
        package for package in sorted(packages, key=key, reverse=True)
        if not filter or any(isinstance(package, package_cls) for package_cls in self._precedence)]
