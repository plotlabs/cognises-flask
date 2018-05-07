from setuptools import setup


setup(name='cognises',
      version='0.3',
      description='Implement application and cloud resource level authorization'
                  ' based on user groups.',
      classifiers=[
          'Programming Language :: Python :: 2.7'
      ],
      url='https://github.com/plotlabs/cognises.git',
      keywords=["aws", "cognito", "security", "authorization", "flask login",
                "flask"],
      author='Shalini Aggarwal',
      author_email='aggarwalshalini1993@gmail.com',
      license='LICENSE.txt',
      packages=['cognises'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['Flask', 'boto3', 'requests', 'simplejson',
                        'python-jose']
      )
