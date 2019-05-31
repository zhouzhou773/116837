import sys
sys.path.append('../packages/reward_gen/build')
from pyreward_gen import *
from pypcsimplus import *
import pypcsimplus as pcsim
from numpy import *
import numpy

class Biofeed(pcsim.Model):
    
    def defaultParameters(self):
        p = self.params
        ep = self.expParams         
        
        p.NumSyn = 100
        
        p.numAdditionalTargetSynapses = 10
        
        p.scaleAdditionalTargetSynapses = 0.5
        
        p.ratioStrong = 0.5
        
        p.numInhibSynapses = 0
        
        # STDP Parameters
        p.Mu = 0.00025 
        p.alpha = 1.05
        p.stdpTaupos = 30e-3
        p.stdpTauneg = 30e-3
        p.stdpGap = 5e-4
        
        # Dopamine Modulated STDP Parameters
        p.DATraceDelay = 0.0
        p.DATraceTau = 0.4 
        p.DAStdpRate = 3 
        p.DATraceShape = 'alpha'
        
        # Kappa kernel
        p.rewardDelay = 0.4
        p.KappaAlpha = 1.01
        p.KappaTaupos = 30e-3
        p.KappaTauneg = 30e-3
        p.KappaTaupos2 = 4e-3
        p.KappaTauneg2 = 4e-3
        p.KappaTauposSquare = 50e-3
        p.KappaTaunegSquare = 50e-3
        p.KappaGap = 1e-4
        p.KappaTe = 1e-3
        p.KernelType = 'DblExp'
                
        p.KappaAnegSquare = -1.0
        
        # synapse parameters
        p.synTau = 5e-3    
        p.delaySyn = 1e-3
        p.U = 0.5
        p.D = 1.1
        p.F = 0.02
        p.Uinh = 0.25
        p.Dinh = 0.7
        p.Finh = 0.02
        p.ErevExc = 0.0
        p.ErevInh = -75e-3
        
        # Neuron parameters 
        p.Cm = 3e-10
        p.Rm = 1e8 
                
        # some problem
        p.Vthresh = - 59e-3
        p.Vresting = - 70e-3    
        p.Trefract = 5e-3
        p.Iinject = 0 
        p.Rbase = 0 # 1.2e-9
        
        p.Wscale = 0.44
        p.WExcScale = 1.0
        p.WInhScale = 1.0
        
        p.currWscale = 0.28
        p.currWExcScale = 1.0
        p.currWInhScale = 1.0
        
        p.diminishingNoise = False
        
        p.noiseLevels = [ p.Rbase, p.Rbase * 0.5, p.Rbase * 0.25, 0.0]
        
        p.initLearnWVar = 1.0 / 10
        p.initLearnWBound = 2.0 / 10
        
        p.initInhWMean = 1.0/4
        p.initInhWVar = 1.0/16
        p.initInhWBound = 1.0/8
        
        p.noiseType = 'OU'
        p.OUScale = 1.0
        
        return p
    
    #
    # Generate the model
    #    
    def generate(self):
        p = self.params
        ep = self.expParams
        dm = self.depModels
        m = self.elements
        net = self.net
        
        p.synTauInh = p.synTau
        
        p.Vreset   = p.Vresting
        p.Vinit    = p.Vresting
        
        p.noiseLvlDurations = [ ep.Tsim / 4.0, ep.Tsim / 4.0, ep.Tsim / 4.0, ep.Tsim ]
        
        # setup the weights
        tau_m = p.Cm * p.Rm
        tau_s = p.synTau
        p.weightExc = ((p.Vthresh - p.Vinit) * p.WExcScale * p.Wscale)/ ((p.ErevExc - p.Vinit) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
    
        tau_s = p.synTauInh    
        p.weightInh =  ((p.Vthresh - p.Vinit) * p.WInhScale * p.Wscale)/ (((p.Vinit+ p.Vthresh) / 2 - p.ErevInh) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
        
        
        # setup the weights of current synapses
        tau_m = p.Cm * p.Rm
        tau_s = p.synTau
        p.CurrWeightExc = ((p.Vthresh - p.Vinit) * p.currWExcScale * p.currWscale)/ ( p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
    
        tau_s = p.synTauInh    
        p.CurrWeightInh =  ((p.Vthresh - p.Vinit) * p.currWInhScale * p.currWscale) / ( p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
    
    
        p.Wmax = p.weightExc * 2
        p.WmaxInh = p.weightInh * 2
        
        p.CurrWmax = p.CurrWeightExc * 2
        p.CurrWmaxInh = p.CurrWeightInh * 2
        
        p.numStrongTargetSynapses = int(p.NumSyn * p.ratioStrong)
        p.numWeakTargetSynapses = p.NumSyn - p.numStrongTargetSynapses
        
        p.stdpApos = p.Mu * p.Wmax # is actually multiplication of the learning rate mu and Apos from stdp 
        p.stdpAneg = - p.alpha * p.stdpApos
        
        p.stdpCurrApos = p.Mu * p.CurrWmax # is actually multiplication of the learning rate mu and Apos from stdp 
        p.stdpCurrAneg = - p.alpha * p.stdpCurrApos
                
        
        p.kappaScalePos = p.KappaTauposSquare / (p.KappaTaupos - p.KappaTaupos2)
        p.KappaApos = p.KappaAlpha * p.kappaScalePos
        p.KappaAposSquare = p.KappaAlpha
            
        #kappaScaleNeg = ( KappaTauneg / KappaTauneg2 ) ** ( - KappaTauneg2 / ( KappaTauneg - KappaTauneg2 ) ) \
        #              - ( KappaTauneg / KappaTauneg2 ) ** ( - KappaTauneg / ( KappaTauneg - KappaTauneg2 ) ) 
            
        p.kappaScaleNeg = p.KappaTaunegSquare / (p.KappaTauneg - p.KappaTauneg2)                  
        p.KappaAneg = - 1.0 * p.kappaScaleNeg
        
        p.Inoise = p.Rbase
        
        p.samplingTime = int(ep.Tsim / (200 * ep.DTsim))  # sampling time for the histogram in number of simulation steps
        
        learnSynW = random.normal(1.0/2 * p.Wmax, p.initLearnWVar * p.Wmax, p.NumSyn)        
        learnSynW.clip( min = (1.0/2 - p.initLearnWBound )* p.Wmax , max = (1.0/2 + p.initLearnWBound )* p.Wmax)
        
        targetSynW = hstack((ones(p.numStrongTargetSynapses) * p.Wmax, zeros(p.numWeakTargetSynapses)))
        
        inhibSynW = random.normal(p.initInhWMean * p.WmaxInh, p.initInhWVar * p.WmaxInh,p.numInhibSynapses) 
        inhibSynW.clip( min = (p.initInhWMean + p.initInhWBound) * p.WmaxInh, max = (p.initInhWMean - p.initInhWBound) * p.WmaxInh)
        
        additionalTargetSynW = p.scaleAdditionalTargetSynapses * ones(p.numAdditionalTargetSynapses) * p.Wmax
        
        print "currWmax = ", p.CurrWmax
        print "Wmax = ", p.Wmax
        
        # ------------------------------------
        learnCurrSynW = list(p.CurrWmax / p.Wmax * array(learnSynW))
            
        targetCurrSynW = [ p.CurrWmax for i in range(p.numStrongTargetSynapses) ] + [ 0.0 for i in range(p.numWeakTargetSynapses) ]
        
        inhibCurrSynW = list(- p.CurrWmaxInh / p.WmaxInh * array(inhibSynW))     
        
        additionalTargetCurrSynW = [ p.CurrWmax for i in range(p.numAdditionalTargetSynapses) ]
                
        
        #*************************************
        # Setup the neurons
        #*************************************
        
        m.learning_nrn = net.add(DARecvCbLifNeuron(Cm = p.Cm, 
                                                 Rm = p.Rm, 
                                                 Vresting = p.Vresting, 
                                                 Vthresh  = p.Vthresh, 
                                                 Vreset   = p.Vreset, 
                                                 Vinit    = p.Vinit, 
                                                 Trefract = p.Trefract, 
                                                 Iinject = 0, 
                                                 Inoise = p.Inoise), SimEngine.ID(0, 0 % (net.maxLocalEngineID() + 1)) )
        
        if p.noiseType == 'OU':
            net.mount(OUNoiseSynapse(0.012e-6 * p.OUScale, 0.003e-6 * p.OUScale, 2.7e-3, 0.0), m.learning_nrn)
            net.mount(OUNoiseSynapse(0.057e-6 * p.OUScale, 0.0066e-6 * p.OUScale, 10.5e-3,-75e-3), m.learning_nrn)
        
        
        m.learning_curr_nrn = net.add(DARecvLifNeuron(Cm = p.Cm, 
                                                     Rm = p.Rm, 
                                                     Vresting = p.Vresting, 
                                                     Vthresh  = p.Vthresh, 
                                                     Vreset   = p.Vreset, 
                                                     Vinit    = p.Vinit, 
                                                     Trefract = p.Trefract, 
                                                     Iinject = 0, 
                                                     Inoise = p.Inoise), SimEngine.ID(0, 1 % (net.maxLocalEngineID() + 1)))
        
        
        m.target_nrn = net.add(CbLifNeuron(Cm = p.Cm, 
                                         Rm = p.Rm, 
                                         Vresting = p.Vresting, 
                                         Vthresh  = p.Vthresh, 
                                         Vreset   = p.Vreset, 
                                         Vinit    = p.Vinit, 
                                         Trefract = p.Trefract), SimEngine.ID(0, 2 % (net.maxLocalEngineID() + 1)))
        
        m.target_curr_nrn = net.add(LifNeuron(Cm = p.Cm, 
                                            Rm = p.Rm, 
                                            Vresting = p.Vresting, 
                                            Vthresh  = p.Vthresh, 
                                            Vreset   = p.Vreset, 
                                            Vinit    = p.Vinit, 
                                            Trefract = p.Trefract), SimEngine.ID(0, 3 % (net.maxLocalEngineID() + 1)))
        
        
        
        # Connect the learning and target neurons to the circuit
        if p.DATraceShape == 'alpha':
            DATraceResponse = AlphaFunctionSpikeResponse(p.DATraceTau)
        else:
            DATraceResponse = ExponentialDecaySpikeResponse(p.DATraceTau)
            
        exc_permutation = numpy.random.permutation(dm.exc_nrn_popul.size())
            
        read_exc_nrns = exc_permutation[:p.NumSyn]
        
        addit_read_exc_nrns = exc_permutation[p.NumSyn:(p.NumSyn + p.numAdditionalTargetSynapses)]
        
        read_inh_nrns = numpy.random.permutation(dm.inh_nrn_popul.size())[:p.numInhibSynapses]
        
        # ******************************** Add learning synapses to learning_nrn
        m.learning_plastic_syn = []        
        for i in xrange(p.NumSyn):
            m.learning_plastic_syn.append(net.connect(dm.exc_nrn_popul[read_exc_nrns[i]], m.learning_nrn, DAModStdpDynamicCondExpSynapse2(
                                                                                          Winit= learnSynW[i], 
                                                                                          tau = p.synTau, 
                                                                                          delay = p.delaySyn, 
                                                                                          Erev = p.ErevExc, 
                                                                                          U = p.U, 
                                                                                          D = p.D, 
                                                                                          F = p.F, 
                                                                                          Wex = p.Wmax, 
                                                                                          activeDASTDP = True, 
                                                                                          STDPgap = p.stdpGap, 
                                                                                          Apos = p.stdpApos, 
                                                                                          Aneg = p.stdpAneg, 
                                                                                          taupos = p.stdpTaupos, 
                                                                                          tauneg = p.stdpTauneg,
                                                                                          DAStdpRate = p.DAStdpRate, 
                                                                                          useFroemkeDanSTDP = False, 
                                                                                          daTraceResponse = DATraceResponse)))
            
        
        m.learning_curr_plastic_syn = []        
        for i in xrange(p.NumSyn):
            m.learning_curr_plastic_syn.append(net.connect(dm.exc_nrn_popul[read_exc_nrns[i]], m.learning_curr_nrn, DAModStdpDynamicCurrExpSynapse2(
                                                                                          Winit= learnCurrSynW[i], 
                                                                                          tau = p.synTau, 
                                                                                          delay = p.delaySyn,
                                                                                          U = p.U, 
                                                                                          D = p.D, 
                                                                                          F = p.F, 
                                                                                          Wex = p.CurrWmax, 
                                                                                          activeDASTDP = True, 
                                                                                          STDPgap = p.stdpGap, 
                                                                                          Apos = p.stdpCurrApos, 
                                                                                          Aneg = p.stdpCurrAneg, 
                                                                                          taupos = p.stdpTaupos, 
                                                                                          tauneg = p.stdpTauneg,
                                                                                          DAStdpRate = p.DAStdpRate, 
                                                                                          useFroemkeDanSTDP = False, 
                                                                                          daTraceResponse = DATraceResponse)))
                
                                                                                          
        
        m.target_syn = []
        for i in xrange(p.NumSyn):
            m.target_syn.append(net.connect(dm.exc_nrn_popul[read_exc_nrns[i]], m.target_nrn, DynamicCondExpSynapse(W = targetSynW[i], 
                                                                                                 delay = p.delaySyn, 
                                                                                                 tau = p.synTau, 
                                                                                                 Erev = p.ErevExc, 
                                                                                                 U = p.U, 
                                                                                                 D = p.D, 
                                                                                                 F = p.F)))
            
        m.target_curr_syn = []
        for i in xrange(p.NumSyn):
            m.target_curr_syn.append(net.connect(dm.exc_nrn_popul[read_exc_nrns[i]], m.target_curr_nrn, DynamicCurrExpSynapse(W = targetCurrSynW[i], 
                                                                                                  delay = p.delaySyn, 
                                                                                                  tau = p.synTau, 
                                                                                                  U = p.U, 
                                                                                                  D = p.D, 
                                                                                                  F = p.F)))
        
            
        m.addit_target_syn = []
        for i in xrange(p.numAdditionalTargetSynapses):
            m.addit_target_syn.append(net.connect(dm.exc_nrn_popul[addit_read_exc_nrns[i]], m.target_nrn, DynamicCondExpSynapse(W = additionalTargetSynW[i], 
                                                                                                 delay = p.delaySyn, 
                                                                                                 tau = p.synTau, 
                                                                                                 Erev = p.ErevExc, 
                                                                                                 U = p.U, 
                                                                                                 D = p.D, 
                                                                                                 F = p.F)))
        
        m.addit_target_curr_syn = []
        for i in xrange(p.numAdditionalTargetSynapses):
            m.addit_target_curr_syn.append( net.connect( dm.exc_nrn_popul[addit_read_exc_nrns[i]], 
                                                         m.target_curr_nrn, DynamicCurrExpSynapse( W = additionalTargetCurrSynW[i], 
                                                                                                 delay = p.delaySyn, 
                                                                                                 tau = p.synTau, 
                                                                                                 U = p.U, 
                                                                                                 D = p.D, 
                                                                                                 F = p.F ) ) )
                
        m.inhib_learn_syn = []
        for i in xrange(p.numInhibSynapses):
            m.inhib_learn_syn.append(net.connect(dm.inh_nrn_popul[read_inh_nrns[i]], m.learning_nrn, DynamicCondExpSynapse(W = inhibSynW[i], 
                                                                                                 delay = p.delaySyn, 
                                                                                                 tau = p.synTauInh, 
                                                                                                 Erev = p.ErevInh, 
                                                                                                 U = p.Uinh, 
                                                                                                 D = p.Dinh, 
                                                                                                 F = p.Finh)))
            
        m.inhib_curr_learn_syn = []
        for i in xrange(p.numInhibSynapses):
            m.inhib_curr_learn_syn.append(net.connect(dm.inh_nrn_popul[read_inh_nrns[i]], m.learning_curr_nrn, DynamicCurrExpSynapse(W = inhibCurrSynW[i], 
                                                                                                                             delay = p.delaySyn, 
                                                                                                                             tau = p.synTauInh,
                                                                                                                             U = p.Uinh, 
                                                                                                                             D = p.Dinh, 
                                                                                                                             F = p.Finh)))
        
            
            
        m.inhib_target_syn = []
        for i in xrange(p.numInhibSynapses):
            m.inhib_target_syn.append(net.connect(dm.inh_nrn_popul[read_inh_nrns[i]], m.target_nrn, DynamicCondExpSynapse(W = inhibSynW[i], 
                                                                                                 delay = p.delaySyn, 
                                                                                                 tau = p.synTauInh, 
                                                                                                 Erev = p.ErevInh, 
                                                                                                 U = p.Uinh, 
                                                                                                 D = p.Dinh, 
                                                                                                 F = p.Finh)))
        
        m.inhib_target_curr_syn = []
        for i in xrange(p.numInhibSynapses):
            m.inhib_target_curr_syn.append(net.connect(dm.inh_nrn_popul[read_inh_nrns[i]], m.target_curr_nrn, DynamicCurrExpSynapse(W = inhibCurrSynW[i], 
                                                                                                                             delay = p.delaySyn, 
                                                                                                                             tau = p.synTauInh,
                                                                                                                             U = p.Uinh, 
                                                                                                                             D = p.Dinh, 
                                                                                                                             F = p.Finh)))
        
        # Create the reward generator and connect it in the circuit
                         
        if p.KernelType == 'alpha':
            rewardGenFactory = BioFeedRewardGenAlpha(Apos = KappaApos, 
                                                      Aneg = p.KappaAneg, 
                                                      taupos = p.KappaTaupos, 
                                                      tauneg = p.KappaTauneg, 
                                                      Gap = p.KappaGap, 
                                                      Te = p.KappaTe)
        elif p.KernelType == "DblExp":
            rewardGenFactory = BioFeedRewardGenDblExp(Apos = p.KappaApos, 
                                                        Aneg = p.KappaAneg, 
                                                        taupos1 = p.KappaTaupos, 
                                                        tauneg1 = p.KappaTauneg, 
                                                        taupos2 = p.KappaTaupos2, 
                                                        tauneg2 = p.KappaTauneg2, 
                                                        Gap = p.KappaGap, 
                                                        Te = p.KappaTe)      
        else:
            rewardGenFactory = BioFeedRewardGen(Apos = p.KappaApos, 
                                                        Aneg = p.KappaAneg, 
                                                        taupos = p.KappaTaupos, 
                                                        tauneg = p.KappaTauneg, 
                                                        Gap = p.KappaGap, 
                                                        Te = p.KappaTe)
            
            
        m.reward_gen = net.add(rewardGenFactory, SimEngine.ID(0, 0))
        
        net.connect(m.learning_nrn, 0, m.reward_gen, 1, Time.sec(ep.minDelay))
        
        net.connect(m.target_nrn, 0, m.reward_gen, 0, Time.sec(ep.minDelay))
        
        net.connect(m.reward_gen, 0, m.learning_nrn, 0, Time.sec(p.rewardDelay))
        
        # ------------------------------
        
        m.reward_gen_curr = net.add(rewardGenFactory, SimEngine.ID(0, 1 % (net.maxLocalEngineID() + 1)) )
        
        net.connect(m.learning_curr_nrn, 0, m.reward_gen_curr, 1, Time.sec(ep.minDelay))
        
        net.connect(m.target_curr_nrn, 0, m.reward_gen_curr, 0, Time.sec(ep.minDelay))
        
        net.connect(m.reward_gen_curr, 0, m.learning_curr_nrn, 0, Time.sec(p.rewardDelay))
        
        
        if p.diminishingNoise:
            m.noise_level_nrn = net.add( AnalogLevelBasedInputNeuron( p.noiseLevels, p.noiseLvlDurations ) , SimEngine.ID(0, 0) )
            net.connect( m.noise_level_nrn, 0, m.learning_nrn , 'Inoise', Time.sec(ep.minDelay) )
            net.connect( m.noise_level_nrn, 0, m.learning_curr_nrn , 'Inoise', Time.sec(ep.minDelay) )
        
        return self.elements
        

    def setupRecordings(self):
        m = self.elements
        p = self.params
        ep = self.expParams
        #
        # Recording all the weights
        # 
        r = Recordings(self.net)
         
        r.weights = SimObjectPopulation(self.net, m.learning_plastic_syn).record(AnalogRecorder(p.samplingTime), "W")         
        r.curr_weights = SimObjectPopulation(self.net, m.learning_curr_plastic_syn).record(AnalogRecorder(p.samplingTime), "W")
        
        # Recorders for the two neurons
        r.target_nrn_spikes = self.net.record(m.target_nrn, SpikeTimeRecorder())
        r.target_curr_nrn_spikes = self.net.record(m.target_curr_nrn, SpikeTimeRecorder())
        
        r.learning_nrn_spikes =  self.net.record(m.learning_nrn, SpikeTimeRecorder())
        r.learning_curr_nrn_spikes =  self.net.record(m.learning_curr_nrn, SpikeTimeRecorder())
        
        return r
    
    def scriptList(self):
        return ["BiofeedModel.py"]