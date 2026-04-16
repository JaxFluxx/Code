package testprotected1;

import testprotectd.Animals;

class Aves extends Animals
{

	private double wingsWidth;
	public Aves(String name, String color,double wingsWidth)
	{
		super(name, color);
		this.wingsWidth=wingsWidth;
	}
	public void info()
	{
		System.out.println("name: "+getName() + "  color: "+color + "  wingsWidth: "+ wingsWidth);
	}
}

class Mammals extends Animals
{

	private double legLength;
	public Mammals(String name, String color,double legLength)
	{
		super(name, color);
		this.legLength=legLength;
	}
	public void info() throws CloneNotSupportedException
	{
		System.out.println("name: "+ getName() + "  color: "+color + "  legLength: "+legLength);
		Aves aves1 =new Aves("eagle","gray",1.2);
		String s=aves1.color;
		aves1.getName();
//		Aves aves2=(Aves)aves1.clone();  //´íÎó
		Mammals m1 =new Mammals("cat", "white", 0.3);
		Mammals m2=(Mammals)m1.clone();
	}
}	

class AnimalsTest
{
	public static void main(String[] args) throws CloneNotSupportedException
	{
		Mammals mamm1=new Mammals("Lion", "yellow ",0.7);
		mamm1.info();
		String s=mamm1.color;
		System.out.println(mamm1.getName());
//		Animals mamm2=mamm1.clone();
	}
}