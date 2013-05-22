# -*- coding: utf-8 -*-

"""PackageSet class"""
from builder.package import Package


class PackageSet(set):

    def __init__(self, package_list=set()):
        # Do merge
        package_list = map(lambda name: \
            Package(name) if isinstance(name, basestring) \
            else name, package_list)
        super(PackageSet, self).__init__(package_list)

    def get_dep_tree(self):
        """Recursively get all dependencides of packages in set."""
        if not len(self):
            return []
        unprocessed = set(self)
        processed = PackageSet()
        while unprocessed:
            for package in list(unprocessed):
                unprocessed |= set(package.deps) - processed
                processed.add(package)
                unprocessed.remove(package)
        return processed

    def merge(self):
        raise NotImplementedError("Does not needed.")
        #package_set = array_unique(package_set);
        #for item in self:
        #    newdata = Package.get_core_package(item)

        #for ($i=0; $i<count($package_set); $i++) {
        #    $newdata = Package.get_core_package($package_set[$i]);
        #    if ($package_set[$i]!==$newdata) {
        #        $package_set[$i] = $newdata;
        #    }
        #}
        #return array_unique($package_set);


    def merge_multi_packages(self):
        # TODO: I have no idea what this function must do
        return PackageSet(self)
