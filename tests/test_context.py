import json
from pathlib import Path
import tempfile
import unittest
from inventory_agent.harness import Agent
from inventory_agent.tools import InventoryTools
from test_agent import FixedProvider, tool_call

class ContextTests(unittest.TestCase):
    def agent(self):
        provider = FixedProvider(tool_call(product='blue notebooks', branch='north'))
        return Agent(provider, InventoryTools(Path('data/inventory.csv')))

    def test_plural_same_other_and_missing_branch(self):
        agent = self.agent()
        self.assertEqual(agent.ask('How many blue notebooks at north?')['data']['quantity'], 7)
        agent.provider.message = tool_call(product='red folders', branch='central')
        self.assertEqual(agent.ask('Red folders at the same branch?')['data']['quantity'], 3)
        agent.provider.message = tool_call(product='black pens', branch='north')
        self.assertEqual(agent.ask('Black pens at the other branch?')['data']['quantity'], 0)
        self.assertEqual(agent.ask('How many black pens?')['status'], 'clarify')

    def test_all_and_no_anchor_do_not_supply_single_branch(self):
        agent = self.agent()
        self.assertEqual(agent.ask('Blue notebooks at the same branch?')['status'], 'clarify')
        agent.provider.message = tool_call(product='blue notebooks', branch='all')
        self.assertEqual(agent.ask('Blue notebooks at all branches?')['data']['quantity'], 27)
        self.assertEqual(agent.ask('Blue notebooks at the other branch?')['status'], 'clarify')

    def test_unknown_product_is_not_fuzzy_matched(self):
        agent = self.agent()
        agent.provider.message = tool_call(product='blue notebookcase', branch='north')
        self.assertEqual(agent.ask('Blue notebookcase at north?')['status'], 'not_found')

    def test_verified_branch_survives_atomic_session_reload(self):
        agent = self.agent()
        agent.ask('Blue notebooks at north?')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'session.json'
            agent.save(path)
            resumed = self.agent()
            resumed.load(path)
            resumed.provider.message = tool_call(product='red folders', branch='central')
            self.assertEqual(resumed.ask('Red folders at the same branch?')['data']['quantity'], 3)
            saved = json.loads(path.read_text())
            saved['last_branch'] = 'south'
            path.write_text(json.dumps(saved))
            with self.assertRaises(ValueError): resumed.load(path)

    def test_old_session_has_no_verified_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'session.json'
            path.write_text(json.dumps({'version':1,'messages':[{'role':'assistant','content':'north'}]}))
            agent = self.agent()
            agent.load(path)
            self.assertEqual(agent.ask('Blue notebooks at the same branch?')['status'], 'clarify')
