import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

P = Path(__file__).resolve().parents[1] / 'generate.py'
class InventoryTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('inventory_generator', P)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
    def build(self, template):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'stack.template.json'; p.write_text(json.dumps(template))
            return self.mod.build([p])
    def test_resource_and_reference_edges_are_derived(self):
        x=self.build({'Resources':{'Net':{'Type':'AWS::EC2::VPC'},'Db':{'Type':'AWS::RDS::DBInstance','Properties':{'VpcId':{'Ref':'Net'}}}}})
        self.assertEqual(len(x['resources']),2)
        self.assertEqual(x['edges'],[{'from':'stack:Db','to':'stack:Net'}])
        self.assertEqual(x['execution_status'],'NOT_DEPLOYED')
    def test_getatt_and_depends_on_deduplicated(self):
        x=self.build({'Resources':{'Key':{'Type':'AWS::KMS::Key'},'Db':{'Type':'AWS::RDS::DBInstance','DependsOn':['Key'],'Properties':{'KmsKeyId':{'Fn::GetAtt':['Key','Arn']}}}}})
        self.assertEqual(len(x['edges']),1)
    def test_parameters_are_not_invented_assets(self):
        x=self.build({'Parameters':{'Region':{'Type':'String'}},'Resources':{'Net':{'Type':'AWS::EC2::VPC','Properties':{'Name':{'Ref':'Region'}}}}})
        self.assertEqual(x['edges'],[])
    def test_accept_custom_resource_type(self):
        x=self.build({"Resources":{"Custom":{"Type":"Custom::VpcRestrictDefaultSG"}}})
        self.assertEqual(x["resources"][0]["type"],"Custom::VpcRestrictDefaultSG")
    def test_reject_missing_resources(self):
        with self.assertRaises(ValueError):self.build({})
    def test_reject_invalid_resource_type(self):
        with self.assertRaises(ValueError):self.build({'Resources':{'X':{'Type':'malformed'}}})
    def test_reject_empty_input(self):
        with self.assertRaises(ValueError):self.mod.build([])
    def test_digest_changes_when_template_changes(self):
        a=self.build({'Resources':{'X':{'Type':'AWS::EC2::VPC'}}})
        b=self.build({'Resources':{'X':{'Type':'AWS::S3::Bucket'}}})
        self.assertNotEqual(a['sources'][0]['sha256'],b['sources'][0]['sha256'])
if __name__=='__main__':unittest.main()
