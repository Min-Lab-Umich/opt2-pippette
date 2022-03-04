from opentrons import protocol_api

# global parameters
metadata = {'protocolName': 'My Protocol',
    'author': 'Name <email@address.com>',
    'description': 'Simple protocol to get started using OT2',
    'apiLevel': '2.11'}


class Lab:

    def __init__(self, protocol, n) -> None:
        self.n = n
        self.protocol = protocol
        # tiprack
        self.tiprack = protocol.load_labware('opentrons_96_filtertiprack_1000ul', '3', label='tiprack')
        # corning_24_wellplate_3.4ml_flat * 3
        self.plates = {}
        plate_locations = [1, 5, 8]
        # set up plates
        self.plates[1] = protocol.load_labware(
            'corning_24_wellplate_3.4ml_flat', location='1', label='plate1')
        for i in [5, 8]:
            self.plates[i] = protocol.load_labware(
                'corning_12_wellplate_6.9ml_flat', location=str(i), label=f'plate{i}')

        # create a pipette
        self.pipette = protocol.load_instrument(
            'p1000_single', mount='left', tip_racks=[self.tiprack])

        # create a trash
        self.trash = protocol.load_labware('agilent_1_reservoir_290ml', '2', label='trash')

        self.reservoir1 = protocol.load_labware('axygen_1_reservoir_90ml', '7', label='water1')
        self.reservoir2 = protocol.load_labware('axygen_1_reservoir_90ml', '4', label='water2')


    def transfer_and_wait(self, where_from, where_to,
                       volume=300, position='A1', waittime=5, 
                       from_reservoir=False):
        self.pipette.pick_up_tip()
        self.protocol.comment("1")
        self.pipette.transfer(volume, where_from.wells_by_name()[position], where_to.wells_by_name()[position], trash=False, new_tip='never')
        self.protocol.comment("2")
        self.protocol.delay(minutes=waittime)
        self.protocol.comment("3")
        if not from_reservoir:
            self.pipette.transfer(volume, where_to.wells(
                position)[0], where_from.wells_by_name()[position], trash=False, new_tip='never')
        else:
            # self.protocol.comment(self.trash.wells_by_name()['B3'])
            self.pipette.transfer(volume, where_to.wells_by_name()[position], self.trash.wells_by_name()['A1'], trash=False, new_tip='never')
        self.protocol.comment("4")
        self.pipette.return_tip()

    def procedure(self):
        for _ in range(self.n):
            # self.pipette.pick_up_tip()
            # 1-1 : 1-4
            self.transfer_and_wait(self.plates[8], self.plates[1])
            # 1-4 : 2-1
            # wash(reservoir1)
            # wash 1
            self.transfer_and_wait(self.reservoir1, self.plates[1], 3e3, 'A1', 1, from_reservoir=True)
            # 2-1 : end
            self.transfer_and_wait(self.plates[5], self.plates[1])
            # wash 2
            self.transfer_and_wait(self.reservoir2, self.plates[1], 3e3, 'A1', 1, from_reservoir=True)
            # wash(reservoir2)
        

# def wash(water_src, where_to=plates[1], position='A1', waittime=1, volume=3e3):
#     # transfer 3ml from water_src to position
# 	pipette.pick_up_tip()
# 	pipette.transfer(volume, water_src, where_to.wells(position))
# 	pipette.delay(minutes=waittime)
# 	pipette.transfer(volume, where_to.wells(position), trash)
# 	pipette.return_tip()



def run(protocol: protocol_api.ProtocolContext):
    protocol.comment("hello, world")
    lab = Lab(protocol=protocol, n=1)
    lab.procedure()
