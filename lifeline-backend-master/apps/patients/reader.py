from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils.translation import ugettext_lazy as _

from apps.patients.forms import PatientForm
from apps.patients.services import create_file_for_patient
from apps.units.services import get_unit_by_name, create_unit
from apps.utils.reader import XslxBaseReader


class XslxPatientReader(XslxBaseReader):
    header_fields_choices = (
        ('full name', 'full_name'),
        ('date of birth\n(2001-01-01)', 'birth_date'),
        ('language\n(e,f,g,s,i,d)', 'language'),
        ('gender\n(f,i,m)', 'gender'),
        ('marital status\n(si,d,h,u,se,w)', 'marital_status'),
        ('identity card number', 'card_number'),
        ('identity document type\n(b_id,b_fn,fn_id)', 'document_type'),
        ('identity card type\n(chi,spo,b/s,par)', 'card_type'),
        ('national register', 'national_register'),
        ('partners name', 'partner_name'),
        ('address', 'address'),
        ('country\nb,bd,bds,ber,bg,bh,bhu,bih,blr,bol,br,brn,\nbru,bs,buf,bur,bvi,c,caf,cam,cd,cdn,cgo,ch,\n'
         'ci,cl,co,cok,com,cpv,cr,cy,cym,cz,d,dji,dk,\ndom,dy,dz,e,eak,eau,eaz,ec,eri,est,et,eth,\n'
         'f,fi,fji,fl,flk,fr,fsm,g,gb,gbz,gca,gdl,geo,\ngh,gnb,gnq,gr,gre,grl,gua,gue,guf,guy,h,\n'
         'hk,hkj,hm,hun,hrv,i,il,ind,ir,irl,irq,is,j,ja,\nk,kaz,kgz,kir,kna,krn,krs,kwt,l,lao,lau,lb,\n'
         'ls,lt,lv,ly,m,ma,mac,mal,mc,mda,mdr,mdv,\nme,mex,mhl,mkd,mli,mnp,moc,mon,mrt,msr,\n'
         'mus,mw,myt,nau,ncl,nep,nfk,nic,niu,nl,nor,\nnz,omn,p,pa,pak,pcn,pe,pl,plw,png,por,ps,py,\n'
         'pyf,qat,ra,rb,rc,rch,reu,rh,ri,rim,rl,rn,ro,rp,\nrs,rsm,ru,rus,rwa,s,sao,sd,sgp,shn,sjm,sk,\n'
         'slb,slo,slv,sme,sn,sod,sp,spm,ssd,stp,swa,\nsy,syr,t,tca,tch,tg,tjk,tkl,tkm,tmp,tn,tog,\n'
         'tr,tt,tuv,tw,u,ukr,usa,uzb,v,vau,vct,vir,vn,\nvza,wag,wal,wan,wd,wl,wlf,wsm,ymm,z,zaf,zim', 'country'),
        ('post code', 'post_code'),
        ('nationality\nb,bd,bds,ber,bg,bh,bhu,bih,blr,bol,br,brn,\nbru,bs,buf,bur,bvi,c,caf,cam,cd,cdn,cgo,ch,\n'
         'ci,cl,co,cok,com,cpv,cr,cy,cym,cz,d,dji,dk,\ndom,dy,dz,e,eak,eau,eaz,ec,eri,est,et,eth,\n'
         'f,fi,fji,fl,flk,fr,fsm,g,gb,gbz,gca,gdl,geo,\ngh,gnb,gnq,gr,gre,grl,gua,gue,guf,guy,h,\n'
         'hk,hkj,hm,hun,hrv,i,il,ind,ir,irl,irq,is,j,ja,\nk,kaz,kgz,kir,kna,krn,krs,kwt,l,lao,lau,lb,\n'
         'ls,lt,lv,ly,m,ma,mac,mal,mc,mda,mdr,mdv,\nme,mex,mhl,mkd,mli,mnp,moc,mon,mrt,msr,\n'
         'mus,mw,myt,nau,ncl,nep,nfk,nic,niu,nl,nor,\nnz,omn,p,pa,pak,pcn,pe,pl,plw,png,por,ps,py,\n'
         'pyf,qat,ra,rb,rc,rch,reu,rh,ri,rim,rl,rn,ro,rp,\nrs,rsm,ru,rus,rwa,s,sao,sd,sgp,shn,sjm,sk,\n'
         'slb,slo,slv,sme,sn,sod,sp,spm,ssd,stp,swa,\nsy,syr,t,tca,tch,tg,tjk,tkl,tkm,tmp,tn,tog,\n'
         'tr,tt,tuv,tw,u,ukr,usa,uzb,v,vau,vct,vir,vn,\nvza,wag,wal,wan,wd,wl,wlf,wsm,ymm,z,zaf,zim', 'nationality'),
        ('foreign register', 'foreign_register'),
        ('telephone', 'phone_number'),
        ('email address', 'email'),
        ('confidential(vip)\n(1,0)', 'is_vip'),
        ('religion\n(adv,aog,bap,bud,cat,\njw,jsh,lut,mrn,no,ort,\noth,pst,qua,isl)', 'religion'),
        ('date of death', 'death_date'),
        ('general practitioner', 'general_practitioner'),
        ('health insurance policy\n(101,102,104,105,106,107,\n108,109,110,111,112,113,114,\n115,116,117,118,119,120,'
         '121,\n122,126,127,128,129,130,131,\n132,133,134,135,136,137,203,\n206,210,216,226,228,230,232,\n235,236,301,'
         '304,305,306,307,\n309,310,311,314,315,316,317,\n319,321,322,323,324,325,327,\n328,401,403,404,407,409,413,\n'
         '414,415,416,417,418,501,506,\n508,509,515,516,522,526,527,\n601,602,603,604,605,606,607,\n608,609,610,612,'
         '615,620,622,\n630,675,690,910,920,921,922,\n930,931,940,941,942,950,951,\n999)', 'insurance_policy'),
        ('heading code hc1/hc2\n(1,2,3,4,7,8)', 'heading_code'),
        ('beneficiary id', 'beneficiary_id'),
        ('beneficiary occupation\n(ph,ptr,prt,ch,oth)', 'beneficiary_occupation'),
        ('unemployed\n(1,0)', 'is_employed'),
        ('dependants\n(no,with)', 'dependants'),
        ('policyholder name', 'policy_holder'),
        ('end of validity period\n(2001-01-01)', 'validity_end'),
        ('authorised third party\n(0,1)', 'is_third_party_auth'),
        ('federal disability recognition\n(1,0)', 'disability_recognition'),
        ('disability assessement points', 'disability_assessment_points'),
        ('regional disability recognition', 'regional_recognition'),
        ('income origin\n(wrk,ant,une,hia,hif,fa,\nsoc,fam,ret,no,oth)', 'income_origin'),
        ('income amount', 'income_amount'),
        ('expenses', 'expenses'),
        ('debts\n(1,0)', 'debts'),
        ('financial power of attorney\n(1,0)', 'attorney'),
        ('financial management', 'management'),
        ('living environment at admission\n(iso,fam,par,shr,oth_fam,ret,\ndis,hm_less,com,jus,oth_com,'
         '\nps_hosp,ps_nurs,slt,plc,alt_ps,\ngen,oth_the,uns,unk)', 'admission'),
        ('current occupation', 'occupation'),
        ('professional career', 'career'),
        ('education\n(nm,sp,nn,un)', 'education'),
        ('education pathway\n(pr,lhs,hs,un,oth,unk)', 'edu_pathway'),
        ('unit', 'unit'),
        ('bed', 'bed'),
    )

    def __init__(self, file, user):
        super().__init__(file)
        self.user = user

    @transaction.atomic
    def proceed(self):
        results = []
        if not self._errors:
            try:
                table = self._wb[self._wb.sheetnames[0]]
                data = list(table)
                if self._not_valid_header(data[0]):
                    self._errors.append(_('File has wrong content'))
                    return
                for row in data[1:]:
                    data = {}
                    for index, item in enumerate(list(row)):
                        if item.value:
                            data[self.header_fields_choices[index][1]] = item.value
                    results.append(data)
                if not results:
                    self._errors.append(self.no_data_error)
                if not self._errors:
                    for result in results:
                        form = PatientForm(result)
                        if form.is_valid():
                            patient = form.save()
                            unit_name = result.get('unit')
                            if unit_name:
                                unit = get_unit_by_name(unit_name) or create_unit(name=unit_name)
                                file = create_file_for_patient(patient, unit.pk)
                                file.bed = result.get('bed')
                                file.save(update_fields=["bed"])
                        else:
                            self._errors.append(form.errors.items())
            except IndexError:
                self._errors.append(self.content_error)
            except (ValidationError, IntegrityError) as error:
                self._errors.append(str(error))
